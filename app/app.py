import reflex as rx
import random
import asyncio
from typing import Generator

INITIAL_PROBLEM_DURATION = 20
BONUS_TIME_PER_CORRECT_ANSWER = 15


class SumPracticeState(rx.State):
    num1: int = 0
    num2: int = 0
    problem_time_left: int = INITIAL_PROBLEM_DURATION
    problem_timer_is_active: bool = False
    apply_bonus_to_next_problem: bool = False

    @rx.var
    def correct_sum(self) -> int:
        return self.num1 + self.num2

    @rx.event
    def initialize_session(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        """Initializes the practice session by starting the first problem."""
        self.apply_bonus_to_next_problem = False
        yield SumPracticeState.start_new_problem

    @rx.event
    def start_new_problem(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        """Sets up a new problem, resets its timer, and starts the countdown."""
        self.num1 = random.randint(10, 99)
        self.num2 = random.randint(10, 99)
        current_duration = INITIAL_PROBLEM_DURATION
        if self.apply_bonus_to_next_problem:
            current_duration += (
                BONUS_TIME_PER_CORRECT_ANSWER
            )
            self.apply_bonus_to_next_problem = False
        self.problem_time_left = current_duration
        self.problem_timer_is_active = True
        yield SumPracticeState.problem_timer_tick

    @rx.event
    def handle_submit(
        self, form_data: dict
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        """Handles answer submission, provides feedback, and moves to the next problem."""
        self.problem_timer_is_active = False
        submitted_value = form_data.get("answer", "")
        feedback_msg = ""
        try:
            answer_int = int(submitted_value)
            if answer_int == self.correct_sum:
                self.apply_bonus_to_next_problem = True
                feedback_msg = f"¡Correcto! +{BONUS_TIME_PER_CORRECT_ANSWER}s para el próximo problema."
            else:
                self.apply_bonus_to_next_problem = False
                feedback_msg = f"Incorrecto. La respuesta era {self.correct_sum}."
        except ValueError:
            self.apply_bonus_to_next_problem = False
            feedback_msg = "Entrada inválida. Por favor, ingresa un número."
        yield rx.toast(
            feedback_msg,
            duration=3000,
            position="top-center",
        )
        yield SumPracticeState.start_new_problem

    @rx.event(background=True)
    async def problem_timer_tick(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        """Background task to countdown time for the current problem."""
        async with self:
            if not self.problem_timer_is_active:
                return
        await asyncio.sleep(1)
        async with self:
            if not self.problem_timer_is_active:
                return
            self.problem_time_left -= 1
            if self.problem_time_left <= 0:
                self.problem_timer_is_active = False
                self.apply_bonus_to_next_problem = False
                yield rx.toast(
                    "¡Tiempo agotado!",
                    duration=3000,
                    position="top-center",
                )
                yield SumPracticeState.start_new_problem
            elif self.problem_timer_is_active:
                yield SumPracticeState.problem_timer_tick


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


def problem_timer_display() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                "Tiempo restante: ",
                class_name="font-medium",
            ),
            rx.el.span(
                SumPracticeState.problem_time_left,
                class_name="font-bold",
            ),
            rx.el.span("s"),
            class_name="text-lg text-gray-700",
        ),
        class_name="fixed top-0 left-0 right-0 bg-white px-6 py-3 shadow-md border-b border-gray-200 z-20 flex justify-center items-center",
    )


def active_practice_screen() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Practica de Sumas",
            class_name="text-3xl font-bold text-indigo-700 mb-8 text-center",
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
        class_name="flex flex-col items-center",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            problem_timer_display(),
            rx.el.div(
                active_practice_screen(),
                class_name="pt-32 pb-10",
            ),
            class_name="relative flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-100 via-indigo-50 to-purple-100 p-4",
        ),
        on_mount=SumPracticeState.initialize_session,
        class_name="font-['Inter']",
    )


head_components = [
    rx.el.title("Practica de Sumas con Bono de Tiempo"),
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
        content="Una aplicación para practicar sumas de nivel primario con un temporizador por problema y un bono de tiempo fijo para el siguiente problema al acertar.",
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