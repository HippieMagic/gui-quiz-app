import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import threading
import time
import random
import logging

# Setup logging
logging.basicConfig(filename='quiz_results.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class QuizQuestion:
    def __init__(self, question_text, answers, correct_answer_index):
        self.question_text = question_text
        self.answers = answers
        self.correct_answer_index = correct_answer_index


class Quiz:
    def __init__(self, master):
        self.master = master
        self.questions = []
        self.time_is_up = False
        self.asked_questions = 0
        self.correct_answers = 0
        self.setup_gui()

    def setup_gui(self):
        self.master.title("Quiz Application")
        start_btn = tk.Button(self.master, text="Start New Quiz", command=self.start_new_quiz)
        start_btn.pack(pady=20)

    def load_questions_from_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        self.questions = []
        current_question = None
        is_reading_question = False
        is_reading_answers = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"):
                continue

            if line.startswith("@Q"):
                is_reading_question = True
                current_question = QuizQuestion("", [], -1)
                continue

            if line.startswith("@A"):
                is_reading_question = False
                is_reading_answers = True
                continue

            if line.startswith("@E"):
                is_reading_answers = False
                self.questions.append(current_question)
                continue

            if is_reading_question:
                current_question.question_text += line + " "
            elif is_reading_answers:
                if line.isdigit():
                    current_question.correct_answer_index = int(line) - 1
                else:
                    current_question.answers.append(line)

        random.shuffle(self.questions)

    def timer(self, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            if self.time_is_up or self.asked_questions >= len(self.questions):
                break
            time.sleep(0.1)  # Check every 0.1 seconds
        if not self.time_is_up:
            self.time_is_up = True
            self.finish_quiz()

    def ask_question(self, question):
        answer = simpledialog.askinteger("Answer the Question",
                                         question.question_text + "\n\n" + "\n".join(
                                             [f"{idx + 1}. {answer}" for idx, answer in enumerate(question.answers)]),
                                         parent=self.master)
        return answer

    def start_quiz(self, num_of_questions, duration):
        self.time_is_up = False
        timer_thread = threading.Thread(target=self.timer, args=(duration,))
        timer_thread.start()

        for i, question in enumerate(self.questions[:num_of_questions]):
            if self.time_is_up:
                break
            answer = self.ask_question(question)
            if answer is None:  # If the dialog is closed, stop the quiz.
                break
            if answer - 1 == question.correct_answer_index:
                self.correct_answers += 1
            self.asked_questions += 1

        if not self.time_is_up:
            self.finish_quiz()

    def finish_quiz(self):
        self.time_is_up = True  # Ensure this is set to prevent further actions
        if self.asked_questions > 0:
            accuracy = (self.correct_answers / self.asked_questions) * 100
        else:
            accuracy = 0
        messagebox.showinfo("Quiz Finished",
                            f"Quiz completed.\nQuestions asked: {self.asked_questions}\nCorrect answers: {self.correct_answers}\nAccuracy: {accuracy:.2f}%")
        logging.info(
            f"Questions asked: {self.asked_questions}, Correct answers: {self.correct_answers}, Accuracy: {accuracy:.2f}%")

    def start_new_quiz(self):
        file_path = filedialog.askopenfilename(title="Select Quiz File",
                                               filetypes=(("Quiz files", "*.q"), ("Text files", "*.txt")))
        if not file_path:
            return
        self.load_questions_from_file(file_path)
        num_of_questions = simpledialog.askinteger("Number of Questions",
                                                   "How many questions would you like to answer?", parent=self.master)
        if not num_of_questions:
            return
        duration = simpledialog.askinteger("Quiz Duration", "Enter the time limit for the quiz in seconds:",
                                           parent=self.master)
        if not duration:
            return

        # Reset quiz statistics
        self.asked_questions = 0
        self.correct_answers = 0

        # Start the quiz with the specified number of questions and duration
        self.start_quiz(num_of_questions, duration)


def main():
    root = tk.Tk()
    app = Quiz(root)
    root.mainloop()


if __name__ == "__main__":
    main()
