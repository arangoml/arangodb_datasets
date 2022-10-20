from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


def progress(
    text: str,
    spinner_name: str = "aesthetic",
    spinner_style: str = "#5BC0DE",
) -> Progress:
    return Progress(
        TextColumn(text),
        SpinnerColumn(spinner_name, spinner_style),
        TimeElapsedColumn(),
        transient=True,
    )
