def interactive_shiritori():
    words = load_words()
    if not words:
        print("単語の読み込みに失敗しました。プログラムを終了します。")
        return

    used_words = set()
    current_word = get_valid_start_word()
    used_words.add(current_word)
    print("スタート単語:", current_word)

    while True:
        valid_candidates = [w for w in words if w not in used_words and is_valid_transition(current_word, w)]
        if not valid_candidates:
            print("プログラム: 次の単語が見つかりません。あなたの勝ちです！")
            break

        program_choice = valid_candidates[0]
        print("プログラムの出力:", program_choice)
        used_words.add(program_choice)
        current_word = program_choice

        while True:
            human_input = input("あなたの番です。単語を入力してください (3文字): ").strip()
            if human_input == "こうさん":
                print("あなたは『こうさん』と入力しました。負けです！")
                break
            if len(human_input) != 3:
                print("エラー: 単語は3文字で入力してください。もう一度入力してください。")
                continue
            if human_input in used_words:
                print("エラー: その単語は既に使用されています。もう一度入力してください。")
                continue
            if not is_valid_transition(current_word, human_input):
                print("エラー: 入力された単語はルールに従っていません。もう一度入力してください。")
                continue
            break

        if human_input == "こうさん":
            break

        used_words.add(human_input)
        current_word = human_input

    again = input("もう一度やりますか？ (y/n): ").strip().lower()
    if again == "y":
        interactive_shiritori()
    else:
        print("ゲーム終了")
