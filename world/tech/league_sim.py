import sys
import csv
import threading
import time


# =============================
# スピナー
# =============================

class Spinner:
    def __init__(self):
        self.running = False
        self.thread = None
        self.pattern_count = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("\rDone.                      ")

    def update_count(self, count):
        self.pattern_count = count

    def _spin(self):
        symbols = "|/-\\"
        idx = 0
        while self.running:
            print(
                f"\rProcessing {symbols[idx % 4]}  Patterns found: {self.pattern_count}",
                end="",
                flush=True,
            )
            idx += 1
            time.sleep(0.1)


# =============================
# 判定ロジック
# =============================

def is_valid_score_sequence(seq, n, d):

    for w in seq:
        if w < 0 or w > d:
            return False

    total_matches = n * d // 2
    if sum(seq) != total_matches:
        return False

    sorted_seq = sorted(seq)
    prefix_sum = 0
    for k in range(1, n + 1):
        prefix_sum += sorted_seq[k - 1]
        if prefix_sum < k * (k - 1) // 2:
            return False

    return True


def generate_sequences(n, writer, spinner):

    d = min(n - 1, 8)
    total_matches = n * d // 2
    pattern_id = 0

    def backtrack(seq, current_sum):
        nonlocal pattern_id

        if len(seq) == n:
            if current_sum == total_matches:
                if is_valid_score_sequence(seq, n, d):
                    pattern_id += 1
                    writer.writerow([pattern_id] + seq)

                    # スピナー更新
                    if pattern_id % 10 == 0:
                        spinner.update_count(pattern_id)
            return

        remaining = n - len(seq)
        min_possible = current_sum
        max_possible = current_sum + remaining * d

        if min_possible > total_matches or max_possible < total_matches:
            return

        for wins in range(d + 1):
            if current_sum + wins > total_matches:
                break
            backtrack(seq + [wins], current_sum + wins)

    backtrack([], 0)
    return pattern_id


# =============================
# メイン
# =============================

def main():

    if len(sys.argv) != 2:
        print("Usage: py league_sim.py [number_of_players]")
        sys.exit(1)

    n = int(sys.argv[1])
    d = min(n - 1, 8)
    filename = f"league_n{n}_max{d}.csv"

    spinner = Spinner()
    spinner.start()

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            header = ["pattern"] + [str(i) for i in range(1, n + 1)]
            writer.writerow(header)

            total = generate_sequences(n, writer, spinner)

    except KeyboardInterrupt:
        spinner.stop()
        print("\nInterrupted.")
        sys.exit(1)

    spinner.stop()
    print(f"Generated {total} patterns.")
    print(f"Saved to {filename}")


if __name__ == "__main__":
    main()
