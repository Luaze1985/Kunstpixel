"""Interactive CLI interface for Kunstpixel (kunstpixel.com) Museumsvert.

Allows museum visitors to chat with the Museumsvert agent in a rich, welcoming terminal interface.
Supports interactive loop, command-line direct queries, and graceful exit.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path for direct script invocation
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from src.aura_museum.core.agent import MuseumsvertAgent


def display_welcome_banner(console: Console) -> None:
    """Display welcoming host banner and instructions."""
    title = Text("🏛️  KUNSTPIXEL (kunstpixel.com)  🏛️", style="bold gold1")
    subtitle = Text(
        "Museumsvert — Interaktiv Publikumsdialog\n"
        "Vennlig, imøtekommende vertskap med direkte tilgang til samlingsdatabasen.",
        style="italic cyan",
    )

    welcome_text = Text()
    welcome_text.append("Hei og hjertelig velkommen til Kunstpixel (kunstpixel.com)!\n\n", style="bold white")
    welcome_text.append(
        "Jeg er din personlige museumsvert. Du kan spørre meg om alt fra hvor du finner bestemte kunstverk,\n"
        "hva som vises i de ulike salene, åpningstider og billettpriser, til personlige anbefalinger dersom\n"
        "du har begrenset med tid.\n\n",
        style="white",
    )
    welcome_text.append("Eksempler på hva du kan spørre om:\n", style="bold yellow")
    welcome_text.append("  • «Hvor finner jeg Skrik?»\n", style="dim white")
    welcome_text.append("  • «Hvor henger bildene til Theodor Kittelsen?»\n", style="dim white")
    welcome_text.append("  • «Hva anbefaler du hvis jeg har 30 minutter?»\n", style="dim white")
    welcome_text.append("  • «Hva koster det for en student og en voksen?»\n", style="dim white")
    welcome_text.append("  • «Når er neste guidet omvisning?»\n", style="dim white")
    welcome_text.append("  • «Har dere noen aktiviteter for barn?»\n\n", style="dim white")
    welcome_text.append("Kommandoer: ", style="bold green")
    welcome_text.append("'hjelp' ", style="cyan")
    welcome_text.append("for hjelpemeny, ", style="white")
    welcome_text.append("'avslutt' / 'exit' ", style="cyan")
    welcome_text.append("for å avslutte samtalen.", style="white")

    panel = Panel(
        welcome_text,
        title=title,
        subtitle=subtitle,
        border_style="bright_blue",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def display_help_table(console: Console) -> None:
    """Display quick reference table with museum rooms and features."""
    table = Table(title="Oversikt over saler og fasiliteter ved Kunstpixel (kunstpixel.com)", border_style="blue")
    table.add_column("Sal / Sted", style="bold cyan", no_wrap=True)
    table.add_column("Etasje", style="magenta", justify="center")
    table.add_column("Tema / Innhold", style="white")
    table.add_column("Sentrale kunstnere", style="green")

    table.add_row(
        "Sal A – Mytologi og natur",
        "1. etasje",
        "Folketro, naturmystikk og nasjonalromantikk",
        "Theodor Kittelsen, Harald Sohlberg, Nikolai Astrup",
    )
    table.add_row(
        "Sal B – Realisme og samfunn",
        "1. etasje",
        "Sosialrealisme, hverdagsliv og samfunnskritikk",
        "Christian Krohg, Erik Werenskiold",
    )
    table.add_row(
        "Sal C – Lys, farge og interiør",
        "2. etasje",
        "Interiørkunst, lysstudier og sommernetter",
        "Harriet Backer, Kitty Kielland, Frits Thaulow",
    )
    table.add_row(
        "Sal D – Eksistens og modernisme",
        "2. etasje",
        "Ekspresjonisme, eksistensiell angst og abstraksjon",
        "Edvard Munch (Skrik), Anna-Eva Bergman",
    )
    table.add_row(
        "Sal E – Temporær utstilling",
        "1. etasje",
        "Skiftende verksteder, foredrag og arrangementer",
        "Aktiviteter og temporære prosjekter",
    )
    table.add_row(
        "Museumskaféen & Butikken",
        "1. etasje",
        "Kaffe, hjemmebakst, lunsj, kunstbøker og plakater",
        "Åpen i museets åpningstid",
    )
    console.print(table)
    console.print()


def main() -> None:
    """Main CLI entrypoint."""
    console = Console()
    agent = MuseumsvertAgent()

    # Handle one-shot CLI query if passed via sys.argv
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip()
        if query in ["--help", "-h"]:
            display_welcome_banner(console)
            display_help_table(console)
            return

        resp = agent.handle_message(query)
        console.print(
            Panel(
                resp.text,
                title="🏛️ Aura Museumsvert",
                subtitle=f"Kategori: {resp.category} | Verktøy: {', '.join(resp.tools_used) or 'ingen'}",
                border_style="green",
            )
        )
        return

    # Interactive chat loop
    display_welcome_banner(console)

    while True:
        try:
            user_input = Prompt.ask("[bold green]Besøkende[/bold green]").strip()
            if not user_input:
                continue

            lower = user_input.lower()
            if lower in ["avslutt", "exit", "quit", "q", "farvel", "ha det"]:
                farewell = Text(
                    "Tusen takk for besøket ved Kunstpixel (kunstpixel.com)!\n"
                    "Håper du har hatt en berikende opplevelse, og velkommen tilbake!",
                    style="italic gold1",
                )
                console.print(Panel(farewell, border_style="gold1"))
                break

            if lower in ["hjelp", "help", "meny"]:
                display_help_table(console)
                continue

            # Process through MuseumsvertAgent
            resp = agent.handle_message(user_input)

            # Format subtitle metadata
            meta_parts = [f"Kategori: {resp.category}"]
            if resp.tools_used:
                meta_parts.append(f"Verktøy: {', '.join(resp.tools_used)}")
            if resp.rooms_referenced:
                meta_parts.append(f"Sal: {', '.join(resp.rooms_referenced)}")
            subtitle_str = " | ".join(meta_parts)

            response_panel = Panel(
                resp.text,
                title="🏛️ Museumsvert",
                subtitle=subtitle_str,
                border_style="green",
                padding=(1, 2),
            )
            console.print()
            console.print(response_panel)
            console.print()

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Avslutter museumsvert-dialogen. Ha en fin dag![/dim]")
            break


if __name__ == "__main__":
    main()