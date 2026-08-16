"""English Duo word bank — CEFR-graded vocabulary (A1-B2).

Each entry has a simple English definition and a natural example sentence.
Distractors for exercises are generated from other entries in the same
level (and same part of speech for fill-in-the-blank).

Levels follow the CEFR scale: A1 (beginner) -> B2 (upper-intermediate).
"""

from __future__ import annotations

from typing import TypedDict

LEVELS = ("a1", "a2", "b1", "b2")


class WordEntry(TypedDict):
    word: str
    pos: str
    definition: str
    example: str
    level: str


WORD_BANK: list[WordEntry] = [
    # ---------------------------------------------------------- A1
    {"word": "apple", "pos": "noun", "definition": "a round fruit with red or green skin", "example": "I eat an apple every day.", "level": "a1"},
    {"word": "book", "pos": "noun", "definition": "a set of printed pages that you read", "example": "She is reading a book.", "level": "a1"},
    {"word": "cat", "pos": "noun", "definition": "a small animal with fur that people keep at home", "example": "The cat is sleeping on the sofa.", "level": "a1"},
    {"word": "dog", "pos": "noun", "definition": "an animal that people keep as a pet", "example": "My dog likes to run in the park.", "level": "a1"},
    {"word": "house", "pos": "noun", "definition": "a building where people live", "example": "They live in a big house.", "level": "a1"},
    {"word": "water", "pos": "noun", "definition": "the clear liquid that you drink", "example": "Can I have a glass of water?", "level": "a1"},
    {"word": "friend", "pos": "noun", "definition": "a person you know and like", "example": "Tom is my best friend.", "level": "a1"},
    {"word": "family", "pos": "noun", "definition": "parents, children, and other close relatives", "example": "My family has four people.", "level": "a1"},
    {"word": "school", "pos": "noun", "definition": "a place where children learn", "example": "The children go to school by bus.", "level": "a1"},
    {"word": "mother", "pos": "noun", "definition": "a female parent", "example": "My mother cooks dinner.", "level": "a1"},
    {"word": "father", "pos": "noun", "definition": "a male parent", "example": "My father works in a bank.", "level": "a1"},
    {"word": "child", "pos": "noun", "definition": "a young person", "example": "The child is playing outside.", "level": "a1"},
    {"word": "morning", "pos": "noun", "definition": "the early part of the day", "example": "I run in the morning.", "level": "a1"},
    {"word": "night", "pos": "noun", "definition": "the time when it is dark outside", "example": "We watch TV at night.", "level": "a1"},
    {"word": "day", "pos": "noun", "definition": "a period of 24 hours", "example": "Have a nice day!", "level": "a1"},
    {"word": "eat", "pos": "verb", "definition": "to put food in your mouth", "example": "We eat breakfast at seven.", "level": "a1"},
    {"word": "drink", "pos": "verb", "definition": "to take liquid into your mouth", "example": "I drink coffee in the morning.", "level": "a1"},
    {"word": "go", "pos": "verb", "definition": "to move from one place to another", "example": "I go to work by train.", "level": "a1"},
    {"word": "work", "pos": "verb", "definition": "to do a job", "example": "She works in a hospital.", "level": "a1"},
    {"word": "play", "pos": "verb", "definition": "to do fun activities", "example": "The kids play football after school.", "level": "a1"},
    {"word": "read", "pos": "verb", "definition": "to look at words and understand them", "example": "I read the news every day.", "level": "a1"},
    {"word": "write", "pos": "verb", "definition": "to make words with a pen or on a keyboard", "example": "Please write your name here.", "level": "a1"},
    {"word": "happy", "pos": "adjective", "definition": "feeling good and pleased", "example": "She is happy with her new job.", "level": "a1"},
    {"word": "big", "pos": "adjective", "definition": "large in size", "example": "They live in a big city.", "level": "a1"},
    {"word": "small", "pos": "adjective", "definition": "little in size", "example": "He has a small car.", "level": "a1"},
    {"word": "red", "pos": "adjective", "definition": "the color of blood", "example": "She wore a red dress.", "level": "a1"},
    {"word": "blue", "pos": "adjective", "definition": "the color of the sky", "example": "The sky is blue today.", "level": "a1"},
    {"word": "good", "pos": "adjective", "definition": "of high quality", "example": "That was a good film.", "level": "a1"},
    {"word": "bad", "pos": "adjective", "definition": "not good", "example": "The weather was bad yesterday.", "level": "a1"},
    {"word": "hello", "pos": "exclamation", "definition": "a word you say when you meet someone", "example": "Hello! How are you?", "level": "a1"},
    # ---------------------------------------------------------- A2
    {"word": "travel", "pos": "verb", "definition": "to go to another place or country", "example": "I want to travel to Japan.", "level": "a2"},
    {"word": "weather", "pos": "noun", "definition": "the condition of the air, such as sun, rain, or wind", "example": "The weather is cold today.", "level": "a2"},
    {"word": "weekend", "pos": "noun", "definition": "Saturday and Sunday", "example": "What do you do on the weekend?", "level": "a2"},
    {"word": "breakfast", "pos": "noun", "definition": "the first meal of the day", "example": "I have eggs for breakfast.", "level": "a2"},
    {"word": "market", "pos": "noun", "definition": "a place where people buy and sell things", "example": "We buy fruit at the market.", "level": "a2"},
    {"word": "neighbor", "pos": "noun", "definition": "a person who lives near you", "example": "Our neighbor has a garden.", "level": "a2"},
    {"word": "question", "pos": "noun", "definition": "something you ask", "example": "I have a question about the homework.", "level": "a2"},
    {"word": "borrow", "pos": "verb", "definition": "to take something and return it later", "example": "Can I borrow your pen?", "level": "a2"},
    {"word": "repair", "pos": "verb", "definition": "to fix something that is broken", "example": "He repaired my bicycle.", "level": "a2"},
    {"word": "invite", "pos": "verb", "definition": "to ask someone to come to an event", "example": "She invited us to her party.", "level": "a2"},
    {"word": "suggest", "pos": "verb", "definition": "to give someone an idea", "example": "I suggest taking a taxi.", "level": "a2"},
    {"word": "promise", "pos": "verb", "definition": "to say firmly that you will do something", "example": "I promise to call you.", "level": "a2"},
    {"word": "decide", "pos": "verb", "definition": "to choose something after thinking", "example": "She decided to study abroad.", "level": "a2"},
    {"word": "forget", "pos": "verb", "definition": "to not remember something", "example": "Don't forget your keys!", "level": "a2"},
    {"word": "remember", "pos": "verb", "definition": "to keep something in your mind", "example": "I remember our first trip.", "level": "a2"},
    {"word": "believe", "pos": "verb", "definition": "to think that something is true", "example": "I believe you.", "level": "a2"},
    {"word": "explain", "pos": "verb", "definition": "to make something clear and easy to understand", "example": "Can you explain this word?", "level": "a2"},
    {"word": "answer", "pos": "verb", "definition": "to say something after a question", "example": "Please answer the question.", "level": "a2"},
    {"word": "teach", "pos": "verb", "definition": "to help someone learn something", "example": "Mr. Lee teaches math.", "level": "a2"},
    {"word": "learn", "pos": "verb", "definition": "to get new knowledge or skills", "example": "I am learning English.", "level": "a2"},
    {"word": "arrive", "pos": "verb", "definition": "to reach a place", "example": "The train arrives at nine.", "level": "a2"},
    {"word": "leave", "pos": "verb", "definition": "to go away from a place", "example": "We leave home at eight.", "level": "a2"},
    {"word": "empty", "pos": "adjective", "definition": "with nothing inside", "example": "The bottle is empty.", "level": "a2"},
    {"word": "full", "pos": "adjective", "definition": "with no space left", "example": "The bus is full.", "level": "a2"},
    {"word": "cheap", "pos": "adjective", "definition": "low in price", "example": "This restaurant is cheap.", "level": "a2"},
    {"word": "expensive", "pos": "adjective", "definition": "high in price", "example": "That hotel is very expensive.", "level": "a2"},
    {"word": "busy", "pos": "adjective", "definition": "having a lot of things to do", "example": "I am busy on Mondays.", "level": "a2"},
    {"word": "quiet", "pos": "adjective", "definition": "with very little noise", "example": "The library is quiet.", "level": "a2"},
    {"word": "careful", "pos": "adjective", "definition": "giving attention to avoid mistakes", "example": "Be careful on the stairs.", "level": "a2"},
    {"word": "lucky", "pos": "adjective", "definition": "having good things happen to you", "example": "You are lucky to have that job.", "level": "a2"},
    # ---------------------------------------------------------- B1
    {"word": "opportunity", "pos": "noun", "definition": "a chance to do something", "example": "This job is a great opportunity.", "level": "b1"},
    {"word": "experience", "pos": "noun", "definition": "knowledge or skill from doing things", "example": "He has ten years of experience.", "level": "b1"},
    {"word": "environment", "pos": "noun", "definition": "the natural world around us", "example": "We must protect the environment.", "level": "b1"},
    {"word": "culture", "pos": "noun", "definition": "the customs, ideas, and art of a group of people", "example": "I love learning about other cultures.", "level": "b1"},
    {"word": "success", "pos": "noun", "definition": "achieving what you wanted to achieve", "example": "Hard work brought her success.", "level": "b1"},
    {"word": "challenge", "pos": "noun", "definition": "something difficult that tests your ability", "example": "Learning a language is a challenge.", "level": "b1"},
    {"word": "achieve", "pos": "verb", "definition": "to succeed in doing something after effort", "example": "She achieved her goal.", "level": "b1"},
    {"word": "improve", "pos": "verb", "definition": "to make something better or become better", "example": "I want to improve my writing.", "level": "b1"},
    {"word": "support", "pos": "verb", "definition": "to help someone or something", "example": "My friends supported me during exams.", "level": "b1"},
    {"word": "argue", "pos": "verb", "definition": "to speak angrily because you disagree", "example": "They argued about money.", "level": "b1"},
    {"word": "admit", "pos": "verb", "definition": "to say that something is true, even if it is bad", "example": "He admitted his mistake.", "level": "b1"},
    {"word": "attempt", "pos": "verb", "definition": "to try to do something", "example": "She attempted the climb twice.", "level": "b1"},
    {"word": "avoid", "pos": "verb", "definition": "to stay away from something", "example": "Avoid eating too much sugar.", "level": "b1"},
    {"word": "deserve", "pos": "verb", "definition": "to be worthy of something", "example": "You deserve a break.", "level": "b1"},
    {"word": "develop", "pos": "verb", "definition": "to grow or improve over time", "example": "The city developed quickly.", "level": "b1"},
    {"word": "encourage", "pos": "verb", "definition": "to give someone confidence to do something", "example": "My teacher encouraged me to speak.", "level": "b1"},
    {"word": "expect", "pos": "verb", "definition": "to think that something will happen", "example": "I expect the bus at noon.", "level": "b1"},
    {"word": "fail", "pos": "verb", "definition": "to not succeed", "example": "He failed the driving test.", "level": "b1"},
    {"word": "insist", "pos": "verb", "definition": "to say firmly that something is true or must happen", "example": "She insisted on paying.", "level": "b1"},
    {"word": "offer", "pos": "verb", "definition": "to give something or help to someone", "example": "They offered me a job.", "level": "b1"},
    {"word": "prefer", "pos": "verb", "definition": "to like one thing more than another", "example": "I prefer tea to coffee.", "level": "b1"},
    {"word": "refuse", "pos": "verb", "definition": "to say no to something", "example": "He refused to answer.", "level": "b1"},
    {"word": "require", "pos": "verb", "definition": "to need something", "example": "This job requires patience.", "level": "b1"},
    {"word": "survive", "pos": "verb", "definition": "to stay alive", "example": "Few plants survive in the desert.", "level": "b1"},
    {"word": "warn", "pos": "verb", "definition": "to tell someone about danger or a problem", "example": "They warned us about the ice.", "level": "b1"},
    {"word": "compare", "pos": "verb", "definition": "to look at how things are similar or different", "example": "Compare the two prices.", "level": "b1"},
    {"word": "complain", "pos": "verb", "definition": "to say that you are unhappy about something", "example": "She complained about the noise.", "level": "b1"},
    {"word": "concentrate", "pos": "verb", "definition": "to give all your attention to something", "example": "I can't concentrate with this music.", "level": "b1"},
    {"word": "responsible", "pos": "adjective", "definition": "having a duty to take care of something", "example": "Parents are responsible for their children.", "level": "b1"},
    {"word": "threaten", "pos": "verb", "definition": "to say you will cause harm or trouble", "example": "The storm threatened the village.", "level": "b1"},
    # ---------------------------------------------------------- B2
    {"word": "significant", "pos": "adjective", "definition": "important or large enough to notice", "example": "There was a significant change in sales.", "level": "b2"},
    {"word": "ambitious", "pos": "adjective", "definition": "wanting to achieve a lot", "example": "She is an ambitious young lawyer.", "level": "b2"},
    {"word": "controversial", "pos": "adjective", "definition": "causing disagreement", "example": "The new law is controversial.", "level": "b2"},
    {"word": "efficient", "pos": "adjective", "definition": "working well without wasting time or energy", "example": "The new system is more efficient.", "level": "b2"},
    {"word": "essential", "pos": "adjective", "definition": "completely necessary", "example": "Water is essential for life.", "level": "b2"},
    {"word": "flexible", "pos": "adjective", "definition": "able to change easily", "example": "My work hours are flexible.", "level": "b2"},
    {"word": "genuine", "pos": "adjective", "definition": "real and honest", "example": "He showed genuine interest.", "level": "b2"},
    {"word": "notorious", "pos": "adjective", "definition": "famous for something bad", "example": "The area is notorious for traffic jams.", "level": "b2"},
    {"word": "sophisticated", "pos": "adjective", "definition": "complex and advanced", "example": "This is a sophisticated piece of software.", "level": "b2"},
    {"word": "sustainable", "pos": "adjective", "definition": "able to continue without harming the future", "example": "We need sustainable energy.", "level": "b2"},
    {"word": "crucial", "pos": "adjective", "definition": "extremely important", "example": "Timing is crucial in this job.", "level": "b2"},
    {"word": "legitimate", "pos": "adjective", "definition": "legal or reasonable", "example": "She had a legitimate complaint.", "level": "b2"},
    {"word": "inevitable", "pos": "adjective", "definition": "impossible to avoid", "example": "Change is inevitable.", "level": "b2"},
    {"word": "profound", "pos": "adjective", "definition": "very deep or strong", "example": "The book had a profound effect on me.", "level": "b2"},
    {"word": "thrive", "pos": "verb", "definition": "to grow and do very well", "example": "Small businesses thrive in this city.", "level": "b2"},
    {"word": "undermine", "pos": "verb", "definition": "to make something weaker", "example": "The rumors undermined her confidence.", "level": "b2"},
    {"word": "advocate", "pos": "verb", "definition": "to support an idea publicly", "example": "They advocate for equal rights.", "level": "b2"},
    {"word": "assess", "pos": "verb", "definition": "to judge the value or quality of something", "example": "The exam assesses your writing.", "level": "b2"},
    {"word": "comprehend", "pos": "verb", "definition": "to understand something fully", "example": "He could not comprehend the instructions.", "level": "b2"},
    {"word": "diminish", "pos": "verb", "definition": "to become smaller or weaker", "example": "His influence diminished over time.", "level": "b2"},
    {"word": "enhance", "pos": "verb", "definition": "to improve or increase something", "example": "The new lights enhance the room.", "level": "b2"},
    {"word": "imply", "pos": "verb", "definition": "to suggest something without saying it directly", "example": "His silence implied agreement.", "level": "b2"},
    {"word": "mitigate", "pos": "verb", "definition": "to make something less harmful", "example": "Trees mitigate the heat in cities.", "level": "b2"},
    {"word": "negotiate", "pos": "verb", "definition": "to discuss in order to reach an agreement", "example": "They negotiated a better price.", "level": "b2"},
    {"word": "persist", "pos": "verb", "definition": "to continue doing something despite difficulty", "example": "If you persist, you will improve.", "level": "b2"},
    {"word": "propose", "pos": "verb", "definition": "to suggest a plan or idea", "example": "He proposed a new schedule.", "level": "b2"},
    {"word": "regulate", "pos": "verb", "definition": "to control something with rules", "example": "The government regulates food safety.", "level": "b2"},
    {"word": "scrutinize", "pos": "verb", "definition": "to examine something very carefully", "example": "The auditors scrutinized every bill.", "level": "b2"},
    {"word": "tolerate", "pos": "verb", "definition": "to accept something unpleasant", "example": "I can't tolerate loud noise.", "level": "b2"},
    {"word": "transform", "pos": "verb", "definition": "to change something completely", "example": "The internet transformed communication.", "level": "b2"},
]


def words_by_level(level: str) -> list[WordEntry]:
    """Return the word bank entries for a CEFR level (a1/a2/b1/b2)."""
    return [w for w in WORD_BANK if w["level"] == level]
