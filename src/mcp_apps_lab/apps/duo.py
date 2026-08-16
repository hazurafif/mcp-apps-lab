"""English Duo app — a Duolingo-style English learning UI.

The LLM-facing entry point is ``duo_english``: it builds a lesson from the
FSRS due queue + new CEFR-graded words (backend: ``mcp_apps_lab.duo``) and
renders interactive exercises in Duolingo's brand look (green/blue/yellow,
Nunito typeface, 3D press buttons). Each answer calls ``grade_answer``
(hashed backend tool) which grades, reschedules the word's FSRS card, and
applies the game mechanics — XP + combo, hearts, daily streak, level ladder.

Lesson flow:
1. Dashboard shows streak / hearts / XP / level progress.
2. Exercises one at a time: "What does X mean?" (MC) or fill-in-the-blank.
3. Instant feedback banner + the example sentence; wrong answers cost a heart.
4. Summary card (or "out of hearts") with a SendMessage back to the chat.
"""

from __future__ import annotations

from fastmcp import FastMCPApp
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool, SendMessage
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Alert,
    AlertDescription,
    AlertTitle,
    Badge,
    Button,
    Card,
    Column,
    Heading,
    If,
    Muted,
    Progress,
    Row,
    Text,
)
from prefab_ui.rx import ERROR, RESULT, Rx
from prefab_ui.themes import Theme

from mcp_apps_lab.duo import build_lesson
from mcp_apps_lab.tools.duo import add_word, get_profile, grade_answer

app = FastMCPApp("English Duo")
app.add_tool(grade_answer)
app.add_tool(get_profile)
app.add_tool(add_word)

# --------------------------------------------------------------------------
# Duolingo brand theme — https://design.duolingo.com
# --------------------------------------------------------------------------

_DUO_GREEN = "#58CC02"
_DUO_GREEN_DARK = "#58A700"
_DUO_BLUE = "#1CB0F6"
_DUO_YELLOW = "#FFC800"
_DUO_RED = "#FF4B4B"
_DUO_TEXT = "#4B4B4B"
_DUO_MASK = "#E5E5E5"
_DUO_GRAY = "#F7F7F7"

_LIGHT_CSS = (
    "--background: #FFFFFF;"
    f" --foreground: {_DUO_TEXT};"
    " --card: #FFFFFF;"
    f" --card-foreground: {_DUO_TEXT};"
    f" --primary: {_DUO_GREEN};"
    " --primary-foreground: #FFFFFF;"
    f" --secondary: {_DUO_GRAY};"
    f" --secondary-foreground: {_DUO_TEXT};"
    f" --muted: {_DUO_GRAY};"
    " --muted-foreground: #777777;"
    " --accent: #D7FFB8;"
    f" --accent-foreground: {_DUO_GREEN_DARK};"
    f" --destructive: {_DUO_RED};"
    " --destructive-foreground: #FFFFFF;"
    f" --border: {_DUO_MASK};"
    f" --input: {_DUO_MASK};"
    f" --ring: {_DUO_GREEN};"
    f" --success: {_DUO_GREEN};"
    f" --warning: {_DUO_YELLOW};"
    f" --info: {_DUO_BLUE};"
    " --radius: 0.75rem;"
)

_DARK_CSS = (
    f"--primary: {_DUO_GREEN_DARK};"
    " --primary-foreground: #FFFFFF;"
    f" --ring: {_DUO_GREEN_DARK};"
    f" --success: {_DUO_GREEN_DARK};"
    f" --warning: {_DUO_YELLOW};"
    f" --destructive: {_DUO_RED};"
    f" --info: {_DUO_BLUE};"
)

# Duolingo's rounded display face (Nunito) + a green 3D "press" CTA shadow.
DUO_THEME = Theme(
    light_css=_LIGHT_CSS,
    dark_css=_DARK_CSS,
    font="Nunito",
)

_CTA_CLASS = "w-full font-extrabold rounded-2xl shadow-[0_4px_0_#58A700]"
_OPTION_CLASS = "w-full justify-start text-left font-bold rounded-2xl py-3"


@app.ui()
def duo_english(level: str = "auto", items: int = 6) -> PrefabApp:
    """Launch an English Duo lesson.

    - level: CEFR level for new words — "auto" (default) picks the level
      with the most due reviews, or the first level with unseen words.
    - items: exercises per lesson (3-10).

    Exercises mix due FSRS reviews with new words; each answer updates the
    word's schedule, XP (+combo bonus), and hearts (5, refill daily).
    """
    lesson = build_lesson(level, items)
    lesson_items = lesson["items"]
    total = len(lesson_items)
    p = lesson["profile"]
    next_xp = p["next_xp"] or 1

    combo = Rx("combo")
    hearts = Rx("hearts")
    xp = Rx("xp")
    index = Rx("index")
    answered = Rx("answered")

    with Column(gap=5, css_class="p-6 max-w-2xl") as view:
        # ------------------------------------------------------ masthead
        with Row(gap=3, align="center"):
            Badge(
                "🦉 English Duo",
                variant="default",
                css_class="px-4 py-2 text-base font-extrabold rounded-2xl",
            )
            Badge("DAILY PRACTICE", variant="outline", css_class="text-xs tracking-widest")

        # ------------------------------------------------------ dashboard
        with Row(gap=3, align="center", wrap=True):
            with If(Rx("streak") > 0):
                Badge(f"🔥 {Rx('streak')}-day streak", variant="warning")
            with If(~(Rx("streak") > 0)):
                Badge("Start a streak!", variant="outline")
            with If(hearts <= 2):
                Badge(f"❤️ {hearts}/5", variant="destructive")
            with If(~(hearts <= 2)):
                Badge(f"❤️ {hearts}/5", variant="secondary")
            Badge(f"⭐ {xp} XP", variant="secondary")
            Badge(f"🏆 {Rx('league')} · Lv {Rx('level')}", variant="outline")

        with Row(gap=3, align="center"):
            Progress(
                value=Rx("level_xp"),
                max=next_xp,
                variant="success",
                size="sm",
                css_class="flex-1",
            )
            Muted(f"{p['level_xp']}/{next_xp} XP to Lv {p['level'] + 1}")

        if total == 0:
            with Card(), Column(gap=3, css_class="p-4"):
                Heading("Nothing to practice right now", level=3)
                Muted(
                    "All words are scheduled. Ask the assistant to add new "
                    "words, or come back when reviews are due."
                )
            return PrefabApp(view=view, state=_initial_state(p, 0), theme=DUO_THEME)

        # ------------------------------------------------------ exercises
        for i, item in enumerate(lesson_items):
            visible = index == i
            is_last = (i + 1) >= total

            with If(visible), Card(), Column(gap=4, css_class="p-4"):
                with Row(align="center", gap=3):
                    Text(
                        f"Exercise {i + 1} of {total}",
                        css_class="text-sm font-bold text-muted-foreground",
                    )
                    Badge(item["level"].upper(), variant="outline")
                    Badge(item["pos"], variant="ghost", css_class="text-xs")
                    with If(combo >= 2):
                        Badge(f"Combo x{combo}", variant="warning")

                Heading(item["prompt"], level=3, css_class="font-extrabold")

                with If(~answered), Column(gap=2):
                    for opt_idx, option in enumerate(item["options"]):
                        Button(
                            option,
                            variant="outline",
                            css_class=_OPTION_CLASS,
                            on_click=CallTool(
                                grade_answer,
                                arguments={
                                    "word": item["word"],
                                    "selected": opt_idx,
                                    "correct": item["correct"],
                                    "combo": str(combo),
                                    "lesson_xp": str(Rx("lesson_xp")),
                                    "lesson_correct": str(Rx("lesson_correct")),
                                    "finished": is_last,
                                },
                                on_success=[
                                    SetState("answered", True),
                                    SetState("last_correct", RESULT.is_correct),
                                    SetState("xp", RESULT.xp_total),
                                    SetState("xp_gain", RESULT.xp_gain),
                                    SetState("combo", RESULT.combo),
                                    SetState("hearts", RESULT.hearts),
                                    SetState("level", RESULT.level),
                                    SetState("league", RESULT.league),
                                    SetState("level_xp", RESULT.level_xp),
                                    SetState("next_xp", RESULT.next_xp),
                                    SetState("streak", RESULT.streak),
                                    SetState("lesson_xp", RESULT.lesson_xp),
                                    SetState("lesson_correct", RESULT.lesson_correct),
                                    SetState("finished", RESULT.finished),
                                    SetState("game_over", RESULT.game_over),
                                ],
                                on_error=ShowToast(ERROR, variant="error"),
                            ),
                        )

                with If(answered), Column(gap=3):
                    for opt_idx, option in enumerate(item["options"]):
                        if opt_idx == item["correct"]:
                            Button(
                                option,
                                variant="success",
                                css_class=_OPTION_CLASS,
                                disabled=True,
                            )
                        else:
                            Button(
                                option,
                                variant="ghost",
                                css_class=f"{_OPTION_CLASS} opacity-50",
                                disabled=True,
                            )
                    with If(Rx("last_correct")), Alert(variant="success"):
                        AlertTitle(f"Correct! +{Rx('xp_gain')} XP")
                        AlertDescription(f"“{item['word']}” — {item['definition']}")
                    with If(~Rx("last_correct")), Alert(variant="destructive"):
                        AlertTitle(f"Not quite — “{item['word']}” means: {item['definition']}")
                        AlertDescription(item["example"])

        # ------------------------------------------------------ next / end
        with If(answered & ~Rx("finished") & ~Rx("game_over")):
            Button(
                "Next Exercise →",
                variant="default",
                css_class=_CTA_CLASS,
                on_click=[
                    SetState("index", index + 1),
                    SetState("answered", False),
                    SetState("last_correct", False),
                ],
            )

        with (
            If(Rx("finished") & ~Rx("game_over")),
            Card(css_class="border-2 border-primary rounded-2xl"),
            Column(gap=3, css_class="p-4 items-center text-center"),
        ):
            Heading("Lesson Complete! 🎉", level=2, css_class="font-extrabold")
            Text(
                f"{Rx('lesson_correct')}/{total} correct · +{Rx('lesson_xp')} XP",
                css_class="text-2xl font-extrabold text-primary",
            )
            Badge(f"🔥 {Rx('streak')}-day streak · ⭐ {Rx('xp')} XP total", variant="warning")
            Muted("Send the results to the conversation to record your progress.")
            Button(
                "Send Results",
                variant="default",
                css_class=_CTA_CLASS,
                on_click=SendMessage(
                    "English Duo lesson complete! "
                    f"Score: {Rx('lesson_correct')}/{total} correct, "
                    f"+{Rx('lesson_xp')} XP (⭐ {Rx('xp')} total), "
                    f"🔥 {Rx('streak')}-day streak, "
                    f"{Rx('league')} league · Level {Rx('level')}."
                ),
            )

        with (
            If(Rx("game_over")),
            Card(css_class="border-2 border-destructive rounded-2xl"),
            Column(gap=3, css_class="p-4 items-center text-center"),
        ):
            Heading("Out of hearts! 💔", level=2, css_class="font-extrabold")
            Text(
                f"{Rx('lesson_correct')}/{total} correct",
                css_class="text-xl font-extrabold text-destructive",
            )
            Muted(
                "Hearts refill every day. Send the results to the "
                "conversation, then come back tomorrow!"
            )
            Button(
                "Send Results",
                variant="outline",
                css_class="w-full font-extrabold rounded-2xl",
                on_click=SendMessage(
                    f"English Duo: out of hearts after {Rx('lesson_correct')}/{total} "
                    f"correct (+{Rx('lesson_xp')} XP). Hearts refill daily."
                ),
            )

    return PrefabApp(view=view, state=_initial_state(p, total), theme=DUO_THEME)


def _initial_state(profile: dict, total: int) -> dict:
    """UI state seeded from the lesson's profile snapshot."""
    return {
        "index": 0,
        "answered": False,
        "last_correct": False,
        "xp": profile["xp"],
        "xp_gain": 0,
        "combo": 0,
        "hearts": profile["hearts"],
        "level": profile["level"],
        "league": profile["league"],
        "level_xp": profile["level_xp"],
        "next_xp": profile["next_xp"] or 1,
        "streak": profile["streak"],
        "lesson_xp": 0,
        "lesson_correct": 0,
        "finished": total == 0,
        "game_over": False,
    }
