import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
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
        self.current_question_index = 0
        self.setup_gui()

    def setup_gui(self):
        self.master.title("Quiz Application")
        start_btn = tk.Button(self.master, text="Start New Quiz", command=self.start_new_quiz)
        start_btn.pack(pady=20)

        # Add a new button to view the log
        view_log_btn = tk.Button(self.master, text="View Log", command=self.view_log)
        view_log_btn.pack(pady=20)

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

    def ask_question(self):
        # Grab the current question
        question = self.questions[self.current_question_index]

        # Increment for the next question
        self.current_question_index += 1

        # Create a Toplevel window to ask the question
        question_window = tk.Toplevel(self.master)
        question_window.wm_title("Question")

        # Display the question text
        tk.Label(question_window, text=question.question_text, wraplength=400).pack(padx=20, pady=10)

        # Variable to hold the index of the selected answer
        selected_answer = tk.IntVar(value=-1)

        # Create a radio button for each answer
        for idx, answer in enumerate(question.answers):
            tk.Radiobutton(question_window, text=answer, variable=selected_answer, value=idx).pack(anchor="w")

        # Function to handle submit action
        def submit_answer():
            question_window.destroy()  # Close the question window
            self.handle_answer(selected_answer.get(), question.correct_answer_index)

        # Submit button
        submit_btn = tk.Button(question_window, text="Submit", command=submit_answer)
        submit_btn.pack(pady=20)

    def handle_answer(self, selected_index, correct_index):
        if selected_index == correct_index:
            self.correct_answers += 1
        self.asked_questions += 1
        if self.asked_questions < len(self.questions) and not self.time_is_up:
            self.ask_question()  # Ask the next question
        else:
            self.finish_quiz()

    def start_quiz(self, num_of_questions, duration):
        self.time_is_up = False
        timer_thread = threading.Thread(target=self.timer, args=(duration,))
        timer_thread.start()

        # Start by asking the first question
        self.ask_question()

    def finish_quiz(self):
        self.time_is_up = True  # Ensure this is set to prevent further actions
        if self.asked_questions > 0:
            accuracy = (self.correct_answers / self.asked_questions) * 100
        else:
            accuracy = 0
        messagebox.showinfo("Quiz Finished",
                            f"Quiz completed.\nQuestions asked: {self.asked_questions}\nCorrect answers: {self.correct_answers}, Accuracy: {accuracy:.2f}%")
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

        # Ensure the number of questions does not exceed the loaded questions
        num_of_questions = min(num_of_questions, len(self.questions))

        # Reset quiz statistics
        self.asked_questions = 0
        self.correct_answers = 0
        self.current_question_index = 0

        # Start the quiz with the specified number of questions and duration
        self.start_quiz(num_of_questions, duration)

    def view_log(self):
        log_window = tk.Toplevel(self.master)
        log_window.title("Quiz Log")
        log_window.geometry("500x400")  # Adjust size as needed

        # Create a Text widget to display the log
        text_area = tk.Text(log_window, wrap="word", state="disabled", bg="light gray")
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

        # Add a scrollbar
        scrollbar = tk.Scrollbar(log_window, command=text_area.yview)
        scrollbar.pack(side="right", fill="y")
        text_area.config(yscrollcommand=scrollbar.set)

        # Read the log file and insert the contents into the Text widget
        with open('quiz_results.log', 'r') as log_file:
            log_contents = log_file.read()
            text_area.config(state="normal")
            text_area.insert("1.0", log_contents)
            text_area.config(state="disabled")  # Prevent editing of log


def main():
    root = tk.Tk()
    app = Quiz(root)
    root.mainloop()


if __name__ == "__main__":
    main()

