import reflex as rx
import random
import asyncio
from typing import Generator

TOTAL_EXERCISES = 15
POINTS_CORRECT = 3
POINTS_INCORRECT = -1
INITIAL_PROBLEM_TIME = 20


class SumPracticeState(rx.State):
    num1: int = 0
    num2: int = 0
    current_exercise_number: int = 0
    score: int = 0
    game_over: bool = False
    problem_time_remaining: int = INITIAL_PROBLEM_TIME
    timer_task_id: int = 0

    @rx.var
    def correct_sum(self) -> int:
        return self.num1 + self.num2

    @rx.event
    def initialize_session(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        self.current_exercise_number = 0
        self.score = 0
        self.game_over = False
        self.timer_task_id += 1
        yield SumPracticeState.start_new_exercise_round

    @rx.event
    def start_new_exercise_round(
        self,
    ) -> (
        Generator[rx.event.EventSpec | None, None, None]
        | None
    ):
        self.current_exercise_number += 1
        if self.current_exercise_number > TOTAL_EXERCISES:
            self.game_over = True
            self.timer_task_id += 1
            return
        self.num1 = random.randint(10, 99)
        self.num2 = random.randint(10, 99)
        self.problem_time_remaining = INITIAL_PROBLEM_TIME
        self.timer_task_id += 1
        return SumPracticeState.run_problem_timer

    @rx.event(background=True)
    async def run_problem_timer(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        current_run_task_id = self.timer_task_id
        while True:
            await asyncio.sleep(1)
            async with self:
                if (
                    self.game_over
                    or self.timer_task_id
                    != current_run_task_id
                ):
                    return
                should_handle_timeout = False
                if self.problem_time_remaining > 0:
                    self.problem_time_remaining -= 1
                if self.problem_time_remaining <= 0:
                    should_handle_timeout = True
            if should_handle_timeout:
                yield SumPracticeState.handle_timeout
                return
            yield

    @rx.event
    def handle_timeout(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        if self.game_over:
            return
        self.score += POINTS_INCORRECT
        yield rx.toast(
            f"¡Tiempo agotado! {POINTS_INCORRECT} punto(s).",
            duration=3000,
            position="top-center",
        )
        yield SumPracticeState.start_new_exercise_round

    @rx.event
    def handle_submit(
        self, form_data: dict
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        if self.game_over:
            return
        self.timer_task_id += 1
        if self.problem_time_remaining <= 0:
            yield rx.toast(
                "El tiempo para este problema ya había terminado.",
                duration=3000,
                position="top-center",
            )
            return
        submitted_value = form_data.get("answer", "")
        toast_props = {
            "duration": 3000,
            "position": "top-center",
        }
        try:
            answer_int = int(submitted_value)
            if answer_int == self.correct_sum:
                self.score += POINTS_CORRECT
                yield rx.toast(
                    f"¡Correcto! +{POINTS_CORRECT} puntos.",
                    **toast_props,
                )
            else:
                self.score += POINTS_INCORRECT
                yield rx.toast(
                    f"Incorrecto. La respuesta era {self.correct_sum}. {POINTS_INCORRECT} punto(s).",
                    **toast_props,
                )
            yield SumPracticeState.start_new_exercise_round
        except ValueError:
            yield rx.toast(
                "Entrada inválida. Por favor, ingresa un número.",
                **toast_props,
            )
            yield SumPracticeState.run_problem_timer


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


def game_status_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                "Ejercicio: ", class_name="font-medium"
            ),
            SumPracticeState.current_exercise_number,
            rx.el.span(f" / {TOTAL_EXERCISES}"),
            class_name="text-lg text-gray-700",
        ),
        rx.el.div(
            rx.icon(
                "clock",
                class_name="h-5 w-5 mr-1 text-gray-600",
            ),
            rx.el.span(
                "Tiempo: ", class_name="font-medium"
            ),
            SumPracticeState.problem_time_remaining,
            rx.el.span("s", class_name="ml-0.5"),
            class_name="text-lg text-gray-700 flex items-center",
        ),
        rx.el.div(
            rx.el.span(
                "Puntuación: ", class_name="font-medium"
            ),
            SumPracticeState.score,
            class_name="text-lg text-gray-700",
        ),
        class_name="fixed top-0 left-0 right-0 bg-white px-6 py-4 shadow-md border-b border-gray-200 z-20 flex justify-between items-center",
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
                key=SumPracticeState.current_exercise_number.to_string()
                + SumPracticeState.num1.to_string()
                + SumPracticeState.num2.to_string(),
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
        class_name="flex flex-col items-center py-10",
    )


def game_over_screen() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "¡Juego Terminado!",
            class_name="text-4xl font-bold text-indigo-700 mb-6 text-center",
        ),
        rx.el.p(
            "Tu puntuación final es: ",
            rx.el.span(
                SumPracticeState.score,
                class_name="font-bold text-2xl text-indigo-600",
            ),
            class_name="text-xl text-gray-800 mb-8 text-center",
        ),
        rx.el.button(
            "Jugar de Nuevo",
            on_click=SumPracticeState.initialize_session,
            class_name="px-10 py-4 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors duration-200 shadow-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 text-lg",
        ),
        class_name="flex flex-col items-center justify-center p-8 bg-white rounded-xl shadow-lg w-full max-w-md",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            game_status_bar(),
            rx.el.div(
                rx.cond(
                    SumPracticeState.game_over,
                    game_over_screen(),
                    active_practice_screen(),
                ),
                class_name="w-full flex flex-col items-center justify-center pt-24 px-4 min-h-[calc(100vh-theme(spacing.24))]",
            ),
            class_name="relative min-h-screen bg-gradient-to-br from-blue-100 via-indigo-50 to-purple-100",
        ),
        on_mount=SumPracticeState.initialize_session,
        class_name="font-['Inter']",
    )


head_components = [
    rx.el.title(
        "Practica de Sumas con Tiempo y Puntuación"
    ),
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
        content="Practica sumas con tiempo límite por problema y puntuación. Los números son de dos dígitos y avanzas al siguiente ejercicio tras cada respuesta.",
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