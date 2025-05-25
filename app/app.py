import reflex as rx
import random
import asyncio
from typing import Generator

PROBLEM_TIME_LIMIT = 20
GAME_TOTAL_TIME = 120


class SumPracticeState(rx.State):
    num1: int = 0
    num2: int = 0
    user_answer: str = ""
    problem_time_left: int = PROBLEM_TIME_LIMIT
    problem_timer_is_active: bool = False
    game_time_left: int = GAME_TOTAL_TIME
    game_timer_is_active: bool = False
    game_over: bool = False
    score: int = 0

    @rx.var
    def correct_sum(self) -> int:
        return self.num1 + self.num2

    @rx.event
    def start_game(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        self.game_over = False
        self.score = 0
        self.game_time_left = GAME_TOTAL_TIME
        self.game_timer_is_active = True
        yield SumPracticeState.start_new_problem
        yield SumPracticeState.game_timer_tick

    @rx.event
    def start_new_problem(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        if self.game_over:
            self.problem_timer_is_active = False
            return
        self.num1 = random.randint(10, 99)
        self.num2 = random.randint(10, 99)
        self.user_answer = ""
        self.problem_time_left = PROBLEM_TIME_LIMIT
        self.problem_timer_is_active = True
        yield SumPracticeState.problem_timer_tick

    @rx.event
    def handle_submit(
        self, form_data: dict
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        if self.game_over:
            return
        self.problem_timer_is_active = False
        answer_str = form_data.get("answer", "")
        self.user_answer = answer_str
        feedback_msg = ""
        try:
            answer_int = int(answer_str)
            if answer_int == self.correct_sum:
                self.score += 3
                feedback_msg = "¡Correcto! +3 Puntos"
            else:
                self.score -= 1
                feedback_msg = f"Incorrecto. La respuesta era {self.correct_sum}. -1 Punto"
        except ValueError:
            self.score -= 1
            feedback_msg = "Entrada inválida. -1 Punto"
            self.user_answer = ""
        yield rx.toast(
            feedback_msg,
            duration=1500,
            position="top-center",
        )
        if not self.game_over:
            yield SumPracticeState.start_new_problem

    @rx.event(background=True)
    async def problem_timer_tick(self):
        async with self:
            if (
                not self.problem_timer_is_active
                or self.game_over
            ):
                return
        await asyncio.sleep(1)
        async with self:
            if (
                not self.problem_timer_is_active
                or self.game_over
            ):
                return
            self.problem_time_left -= 1
            if self.problem_time_left <= 0:
                self.problem_time_left = 0
                self.problem_timer_is_active = False
                yield SumPracticeState.handle_problem_timeout
                return
            elif self.problem_timer_is_active and (
                not self.game_over
            ):
                yield SumPracticeState.problem_timer_tick
                return

    @rx.event
    def handle_problem_timeout(
        self,
    ) -> Generator[rx.event.EventSpec | None, None, None]:
        if self.game_over:
            return
        self.score -= 1
        feedback_msg = f"¡Tiempo del problema agotado! La respuesta era {self.correct_sum}. -1 Punto"
        yield rx.toast(
            feedback_msg,
            duration=2000,
            position="top-center",
        )
        if not self.game_over:
            yield SumPracticeState.start_new_problem

    @rx.event(background=True)
    async def game_timer_tick(self):
        async with self:
            if (
                not self.game_timer_is_active
                or self.game_over
            ):
                return
        await asyncio.sleep(1)
        async with self:
            if not self.game_timer_is_active:
                return
            self.game_time_left -= 1
            if self.game_time_left <= 0:
                self.game_time_left = 0
                self.game_over = True
                self.game_timer_is_active = False
                self.problem_timer_is_active = False
                yield rx.toast(
                    "¡Juego Terminado!",
                    duration=3000,
                    position="top-center",
                )
                return
            elif self.game_timer_is_active:
                yield SumPracticeState.game_timer_tick
                return


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
                "Tiempo Total: ", class_name="font-medium"
            ),
            rx.el.span(
                SumPracticeState.game_time_left,
                class_name="font-bold",
            ),
            rx.el.span("s"),
            class_name="text-lg text-gray-700",
        ),
        rx.el.div(
            rx.el.span(
                "Puntuación: ", class_name="font-medium"
            ),
            rx.el.span(
                SumPracticeState.score,
                class_name="font-bold",
            ),
            class_name="text-lg text-indigo-700",
        ),
        class_name="fixed top-0 left-0 right-0 bg-white px-6 py-3 shadow-md border-b border-gray-200 z-20 flex justify-between items-center",
    )


def game_over_screen() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "¡Juego Terminado!",
            class_name="text-4xl font-bold text-red-600 mb-6",
        ),
        rx.el.p(
            "Tu puntuación final es: ",
            rx.el.span(
                SumPracticeState.score,
                class_name="font-extrabold text-5xl text-indigo-700",
            ),
            class_name="text-3xl text-gray-800 mb-10",
        ),
        rx.el.button(
            "Jugar de Nuevo",
            on_click=SumPracticeState.start_game,
            class_name="px-10 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors duration-200 shadow-lg text-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
        ),
        class_name="flex flex-col items-center justify-center text-center p-8",
    )


def active_game_screen() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Practica de Sumas",
            class_name="text-3xl font-bold text-indigo-700 mb-4 text-center",
        ),
        rx.el.div(
            rx.el.span(
                "Tiempo del problema: ",
                class_name="font-medium text-sm",
            ),
            rx.el.span(
                SumPracticeState.problem_time_left,
                class_name="font-bold text-sm",
            ),
            rx.el.span("s", class_name="text-sm"),
            class_name="text-md text-gray-600 mb-6 text-center",
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
                key=SumPracticeState.num1.to_string()
                + "_"
                + SumPracticeState.num2.to_string(),
                default_value=SumPracticeState.user_answer,
                disabled=SumPracticeState.game_over
                | (SumPracticeState.problem_time_left == 0),
            ),
            rx.el.button(
                "Revisar Respuesta",
                type="submit",
                class_name="mt-6 px-8 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors duration-200 shadow-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2",
                disabled=SumPracticeState.game_over
                | (SumPracticeState.problem_time_left == 0)
                | (SumPracticeState.user_answer == ""),
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
            game_status_bar(),
            rx.el.div(
                rx.cond(
                    SumPracticeState.game_over,
                    game_over_screen(),
                    active_game_screen(),
                ),
                class_name="pt-24 pb-10",
            ),
            class_name="relative flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-100 via-indigo-50 to-purple-100 p-4",
        ),
        on_mount=SumPracticeState.start_game,
        class_name="font-['Inter']",
    )


head_components = [
    rx.el.title("Practica de Sumas Dinámica"),
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
        content="Una aplicación para practicar sumas de nivel primario con tiempo y puntuación.",
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