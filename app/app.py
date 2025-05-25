import reflex as rx
import random
from typing import Generator


class SumPracticeState(rx.State):
    num1: int = 0
    num2: int = 0
    user_answer: str = ""
    feedback_message: str = ""
    feedback_type: str = ""
    attempts_left: int = 2

    @rx.var
    def correct_sum(self) -> int:
        return self.num1 + self.num2

    @rx.event
    def start_new_problem(self) -> None:
        self.num1 = random.randint(1, 9)
        self.num2 = random.randint(1, 9)
        self.user_answer = ""
        self.feedback_message = ""
        self.feedback_type = ""
        self.attempts_left = 2

    @rx.event
    def handle_submit(
        self, form_data: dict
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        answer_str = form_data.get("answer", "")
        self.user_answer = answer_str
        try:
            answer_int = int(answer_str)
            if answer_int == self.correct_sum:
                self.feedback_message = "¡Correcto!"
                self.feedback_type = "success"
                yield rx.toast(
                    "¡Muy bien! Siguiente problema...",
                    duration=1500,
                    position="top-center",
                )
                yield SumPracticeState.start_new_problem
            else:
                self.attempts_left -= 1
                if self.attempts_left > 0:
                    self.feedback_message = "Incorrecto. Te queda 1 intento más."
                    self.feedback_type = "error"
                else:
                    self.feedback_message = f"Fallaste. La respuesta correcta era {self.correct_sum}."
                    self.feedback_type = "error"
                    yield rx.toast(
                        f"La respuesta era {self.correct_sum}. ¡Nuevo problema!",
                        duration=2500,
                        position="top-center",
                    )
                    yield SumPracticeState.start_new_problem
        except ValueError:
            self.feedback_message = (
                "Por favor, ingresa un número válido."
            )
            self.feedback_type = "warning"
            self.user_answer = ""


def number_box(number_var: rx.Var[int]) -> rx.Component:
    return rx.el.div(
        number_var,
        class_name="w-20 h-20 bg-white border-2 border-gray-300 rounded-lg flex items-center justify-center text-4xl font-bold shadow-sm",
    )


def operator_display(operator: str) -> rx.Component:
    return rx.el.span(
        operator,
        class_name="text-4xl font-bold mx-4 text-gray-700",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.h1(
                "Practica de Sumas de Primaria",
                class_name="text-3xl font-bold text-indigo-700 mb-10 text-center",
            ),
            rx.el.div(
                number_box(SumPracticeState.num1),
                operator_display("+"),
                number_box(SumPracticeState.num2),
                operator_display("="),
                class_name="flex items-center justify-center mb-8",
            ),
            rx.el.form(
                rx.el.input(
                    name="answer",
                    placeholder="?",
                    type="number",
                    class_name="w-24 h-20 border-2 border-gray-400 rounded-lg text-center text-4xl font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm",
                    auto_focus=True,
                ),
                rx.el.button(
                    "Revisar Respuesta",
                    type="submit",
                    class_name="mt-6 px-8 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors duration-200 shadow-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2",
                ),
                on_submit=SumPracticeState.handle_submit,
                reset_on_submit=True,
                class_name="flex flex-col items-center",
            ),
            rx.el.p(
                SumPracticeState.feedback_message,
                class_name=rx.match(
                    SumPracticeState.feedback_type,
                    (
                        "success",
                        "text-green-600 mt-6 text-xl font-medium animate-pulse",
                    ),
                    (
                        "error",
                        "text-red-600 mt-6 text-xl font-medium",
                    ),
                    (
                        "warning",
                        "text-yellow-500 mt-6 text-xl font-medium",
                    ),
                    "mt-6 text-xl font-medium h-7",
                ),
            ),
            class_name="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-100 via-indigo-50 to-purple-100 p-4",
        ),
        on_mount=SumPracticeState.start_new_problem,
        class_name="font-['Inter']",
    )


head_components = [
    rx.el.title("Practica de Sumas"),
    rx.el.link(
        rel="preconnect",
        href="https://fonts.googleapis.com",
    ),
    rx.el.link(
        rel="preconnect",
        href="https://fonts.gstatic.com",
        crossorigin="",
    ),
    rx.el.link(
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        rel="stylesheet",
    ),
    rx.el.meta(
        name="description",
        content="Una aplicación para practicar sumas de nivel primario.",
    ),
    rx.el.meta(
        name="viewport",
        content="width=device-width, initial-scale=1",
    ),
    rx.el.link(
        rel="icon", href="/favicon.ico", type="image/x-icon"
    ),
]
app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=head_components,
    html_lang="es",
)
app.add_page(index, route="/")