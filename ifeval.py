import json
import re

class IFEvalChecker:
  """
  IFEvalの評価ロジックを模した判定クラス
  """

  def __init__(self, output_text):
    self.output_text = output_text.strip()
    self.results = []
    self.extracted_json = {}

  def check_json_format(self):
    """制約: JSON形式であること"""
    try:
      # 文字列の中にJSONが含まれているか探す
      match = re.search(r'\{.*\}', self.output_text, re.DOTALL)
      if not match:
        raise ValueError("JSONのブラケット {} が見つかりません")

      json_str = match.group(0)
      self.extracted_json = json.loads(json_str)

      self.results.append(
          {"test": "JSON形式チェック", "status": "PASS", "msg": "有効なJSONです"})
      return True
    except Exception as e:
      self.results.append(
          {"test": "JSON形式チェック", "status": "FAIL", "msg": f"JSONとして読み込めません: {e}"})
      return False

  def check_forbidden_words(self, forbidden_words):
    """制約: 禁止ワードが含まれていないこと"""
    # JSONの中身（storyの値）だけをチェックするか、全体をチェックするか
    # ここでは、より厳密に「抽出されたストーリー本文」をチェックします
    target_text = self.extracted_json.get("story", self.output_text)

    failures = []
    for word in forbidden_words:
      if word in target_text:
        failures.append(word)

    if failures:
      self.results.append({"test": "禁止単語チェック", "status": "FAIL",
                          "msg": f"禁止単語が含まれています: {', '.join(failures)}"})
    else:
      self.results.append(
          {"test": "禁止単語チェック", "status": "PASS", "msg": "禁止単語は含まれていません"})

  def check_length_constraint(self, min_len, max_len):
    """制約: 文字数が指定範囲内であること"""
    target_text = self.extracted_json.get("story", self.output_text)
    length = len(target_text)

    if min_len <= length <= max_len:
      self.results.append({"test": "文字数チェック", "status": "PASS",
                          "msg": f"{length}文字 (範囲内: {min_len}-{max_len})"})
    else:
      self.results.append({"test": "文字数チェック", "status": "FAIL",
                          "msg": f"{length}文字 (範囲外: {min_len}-{max_len})"})

  def show_report(self):
    """結果をコンソールに表示"""
    print("\n" + "=" * 40)
    print("       IFEval 簡易判定レポート")
    print("=" * 40)
    score = 0
    for res in self.results:
      icon = "✅" if res["status"] == "PASS" else "❌"
      print(f"{icon} [{res['test']}] : {res['msg']}")
      if res["status"] == "PASS":
        score += 1

    print("-" * 40)
    print(f"総合スコア: {score} / {len(self.results)}")
    print("=" * 40 + "\n")

# ==========================================
# 【使い方】
# 1. ChatGPTやClaudeに以下のプロンプトを投げてください
#    「浦島太郎のあらすじを教えて。ただし制約として、
#      1. JSON形式 {"story": "..."} で出力
#      2. "浦島太郎"という漢字は絶対使用禁止
#      3. 300文字以上、350文字以下」
#
# 2. 返ってきた答えを下の変数にコピペしてください (トリプルクォートの中)
# ==========================================

# ▼ ここにAIの回答を貼り付ける ▼
llm_response_sample = """
{
  "story": "むかし、うらしまたろうという若者が、浜辺で子どもたちにいじめられていた亀を助けた。すると亀は恩返しとして彼を竜宮城へ案内し、そこで乙姫に迎えられ、豪華な宴でもてなされた。やがて家が恋しくなり帰ることを望むと、乙姫は絶対に開けてはいけないと伝えて玉手箱を渡した。地上へ戻ると村の様子はすっかり変わり、知る人もいなかった。途方に暮れて箱を開けると白い煙が立ちのぼり、彼はたちまち年老いてしまった。"
}


"""
# ▲ ここまで ▲

if __name__ == "__main__":
  # インスタンス化
  checker = IFEvalChecker(llm_response_sample)

  # テスト実行
  # 1. JSONかどうか
  is_json = checker.check_json_format()

  if is_json:
    # 2. 禁止ワード ("浦島太郎")
    checker.check_forbidden_words(["浦島太郎"])

    # 3. 文字数 (300文字以上, 350文字以下)
    checker.check_length_constraint(300, 350)

  # 結果表示
  checker.show_report()
