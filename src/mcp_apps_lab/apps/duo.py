"""English Duo app — a Duolingo-style English learning UI.

The LLM-facing entry point is ``duo_english``: it builds a lesson from the
FSRS due queue + new CEFR-graded words (backend: ``mcp_apps_lab.duo``) and
renders interactive exercises in Duolingo's brand look (green/blue/yellow,
Nunito typeface, 3D press buttons). Five exercise types cycle through each
lesson, so it is never just a multiple-choice quiz:

- ``mc``    — pick the definition of a word
- ``fill``  — pick the word that fits a sentence blank
- ``type``  — TYPE the missing word (no choices at all)
- ``order`` — build the sentence by tapping scrambled word tiles
- ``flip``  — flashcard: flip, then self-rate Again/Hard/Good/Easy

Each answer calls ``grade_answer`` (hashed backend tool) which grades,
reschedules the word's FSRS card, and applies the game mechanics — XP +
combo, hearts, daily streak, level ladder.
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
    Input,
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
_TILE_CLASS = "font-extrabold rounded-2xl px-4 py-2"
_CHECK_CLASS = "flex-1 font-extrabold rounded-2xl shadow-[0_4px_0_#58A700]"


_TYPE_LABELS = {
    "mc": "Multiple choice",
    "fill": "Fill the blank",
    "type": "Type it",
    "order": "Sentence",
    "flip": "Flashcard",
}


def _grade_actions(item: dict, i: int, total: int, extra: dict) -> CallTool:
    """A grade_answer tool call with the shared on_success state sync."""
    is_last = (i + 1) >= total
    return CallTool(
        grade_answer,
        arguments={
            "word": item["word"],
            "exercise_type": item["type"],
            "combo": str(Rx("combo")),
            "lesson_xp": str(Rx("lesson_xp")),
            "lesson_correct": str(Rx("lesson_correct")),
            "finished": is_last,
            **extra,
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
    )


_TOTAL = 1  # replaced below; avoids referencing the loop variable in helpers


@app.ui()
def duo_english(level: str = "auto", items: int = 6) -> PrefabApp:
    """Launch an English Duo lesson.

    - level: CEFR level for new words — "auto" (default) picks the level
      with the most due reviews, or the first level with unseen words.
    - items: exercises per lesson (3-10).

    Exercise types cycle mc → fill → type → order → flip; each answer
    updates the word's FSRS schedule, XP (+combo bonus), and hearts (5,
    refill daily).
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
            return PrefabApp(view=view, state=_initial_state(p, lesson_items), theme=DUO_THEME)

        # ------------------------------------------------------ exercises
        for i, item in enumerate(lesson_items):
            visible = index == i

            with If(visible), Card(), Column(gap=4, css_class="p-4"):
                with Row(align="center", gap=3):
                    Text(
                        f"Exercise {i + 1} of {total}",
                        css_class="text-sm font-bold text-muted-foreground",
                    )
                    Badge(item["level"].upper(), variant="outline")
                    Badge(_TYPE_LABELS[item["type"]], variant="ghost", css_class="text-xs")
                    with If(combo >= 2):
                        Badge(f"Combo x{combo}", variant="warning")

                # ---- multiple choice / fill-the-blank: pick an option
                if item["type"] in ("mc", "fill"):
                    Heading(item["prompt"], level=3, css_class="font-extrabold")
                    with If(~answered), Column(gap=2):
                        for opt_idx, option in enumerate(item["options"]):
                            Button(
                                option,
                                variant="outline",
                                css_class=_OPTION_CLASS,
                                on_click=_grade_actions(
                                    item,
                                    i,
                                    total,
                                    {"selected": opt_idx, "correct": item["correct"]},
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

                # ---- type the word: a real input, no choices
                elif item["type"] == "type":
                    Heading(item["prompt"], level=3, css_class="font-extrabold")
                    Muted(item["hint"])
                    with If(~answered), Column(gap=3):
                        Input(
                            name=f"typed_{i}",
                            placeholder="Type the word…",
                            css_class="w-full font-bold rounded-2xl px-4 py-3",
                        )
                        Button(
                            "Check",
                            variant="default",
                            css_class=_CHECK_CLASS,
                            on_click=_grade_actions(
                                item,
                                i,
                                total,
                                {"selected": str(Rx(f"typed_{i}")), "correct": item["word"]},
                            ),
                        )

                # ---- sentence builder: tap scrambled word tiles in order
                elif item["type"] == "order":
                    Heading(item["prompt"], level=3, css_class="font-extrabold")
                    with If(~answered), Column(gap=3):
                        with Column(
                            gap=1,
                            css_class="min-h-14 justify-center rounded-2xl border-2 border-[#E5E5E5] bg-[#F7F7F7] px-4 py-3",
                        ):
                            with If(Rx(f"answer_{i}") == ""):
                                Muted("Tap the words in order")
                            with If(Rx(f"answer_{i}") != ""):
                                Text(Rx(f"answer_{i}"), css_class="font-bold text-lg")
                        with Row(gap=2, wrap=True):
                            for j, tile_word in enumerate(item["tiles"]):
                                Button(
                                    tile_word,
                                    variant="outline",
                                    disabled=Rx(f"used_{i}_{j}"),
                                    css_class=_TILE_CLASS,
                                    on_click=[
                                        SetState(f"used_{i}_{j}", True),
                                        SetState(
                                            f"answer_{i}", Rx(f"answer_{i}") + " " + tile_word
                                        ),
                                    ],
                                )
                        with Row(gap=2):
                            Button(
                                "Clear",
                                variant="ghost",
                                css_class="font-bold rounded-2xl",
                                on_click=[
                                    SetState(f"answer_{i}", ""),
                                    *[
                                        SetState(f"used_{i}_{j}", False)
                                        for j in range(len(item["tiles"]))
                                    ],
                                ],
                            )
                            Button(
                                "Check",
                                variant="default",
                                css_class=_CHECK_CLASS,
                                on_click=_grade_actions(
                                    item,
                                    i,
                                    total,
                                    {"selected": str(Rx(f"answer_{i}")), "correct": item["target"]},
                                ),
                            )

                # ---- flashcard: flip, then self-rate (FSRS 1-4)
                elif item["type"] == "flip":
                    with (
                        If(~Rx(f"flipped_{i}") & ~answered),
                        Column(gap=3, css_class="items-center text-center"),
                    ):
                        Heading(item["word"], level=2, css_class="font-extrabold text-3xl")
                        Muted("Do you remember what this means?")
                        Button(
                            "Flip card",
                            variant="default",
                            css_class=_CTA_CLASS,
                            on_click=SetState(f"flipped_{i}", True),
                        )
                    with If(Rx(f"flipped_{i}") & ~answered), Column(gap=3):
                        with Card(css_class="bg-[#F7F7F7]"), Column(gap=2, css_class="p-4"):
                            Heading(item["definition"], level=4)
                            Muted(f"📖 {item['example']}")
                        Muted("How well did you know it?")
                        with Row(gap=2):
                            Button(
                                "Again",
                                variant="destructive",
                                css_class=_TILE_CLASS,
                                on_click=_grade_actions(item, i, total, {"rating": 1}),
                            )
                            Button(
                                "Hard",
                                variant="warning",
                                css_class=_TILE_CLASS,
                                on_click=_grade_actions(item, i, total, {"rating": 2}),
                            )
                            Button(
                                "Good",
                                variant="default",
                                css_class=_TILE_CLASS,
                                on_click=_grade_actions(item, i, total, {"rating": 3}),
                            )
                            Button(
                                "Easy",
                                variant="success",
                                css_class=_TILE_CLASS,
                                on_click=_grade_actions(item, i, total, {"rating": 4}),
                            )

                # ---- reveal + feedback (all types)
                with If(answered), Column(gap=3):
                    with If(Rx("last_correct")), Alert(variant="success"):
                        AlertTitle(f"Correct! +{Rx('xp_gain')} XP")
                        AlertDescription(f"“{item['word']}” — {item['definition']}")
                    with If(~Rx("last_correct")), Alert(variant="destructive"):
                        AlertTitle(f"Not quite — “{item['word']}” means: {item['definition']}")
                        AlertDescription(item["example"])
                    if item["type"] == "order":
                        Muted(f"💡 {item['example']}")

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

    return PrefabApp(view=view, state=_initial_state(p, lesson_items), theme=DUO_THEME)


def _initial_state(profile: dict, lesson_items: list[dict]) -> dict:
    """UI state seeded from the lesson's profile snapshot + per-exercise keys."""
    state = {
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
        "finished": len(lesson_items) == 0,
        "game_over": False,
    }
    for i, item in enumerate(lesson_items):
        if item["type"] == "type":
            state[f"typed_{i}"] = ""
        elif item["type"] == "order":
            state[f"answer_{i}"] = ""
            for j in range(len(item["tiles"])):
                state[f"used_{i}_{j}"] = False
        elif item["type"] == "flip":
            state[f"flipped_{i}"] = False
    return state
