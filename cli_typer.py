#!/usr/bin/env python3
"""
TRIAXUS Time Series Plot Generator using Typer

Modern command-line interface for TRIAXUS time series plotting with rich output.
"""

import typer
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Add the project root to the path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from triaxus.visualizer import TriaxusVisualizer
from triaxus.data.simple_data_generator import PlotTestDataGenerator

# Initialize Typer app and Rich console
app = typer.Typer(
    name="triaxus-plot",
    help="TRIAXUS Time Series Plot Generator",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


# Initialize data generator
data_generator = PlotTestDataGenerator()  # Simple data generator for plot testing


def _create_plot_with_progress(
    plot_type: str,
    data: pd.DataFrame,
    output: str,
    verbose: bool,
    title: str = None,
    **kwargs,
) -> str:
    """
    Common function to create plots with progress indicators

    Args:
        plot_type: Type of plot to create
        data: Input data
        output: Output file path
        verbose: Whether to show verbose output
        title: Plot title
        **kwargs: Additional plot parameters

    Returns:
        Output file path
    """
    # Initialize visualizer
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=not verbose,
    ) as progress:
        task = progress.add_task(f"Initializing visualizer...", total=None)
        visualizer = TriaxusVisualizer(theme=kwargs.get("theme", "oceanographic"))

    # Create plot
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=not verbose,
    ) as progress:
        task = progress.add_task(f"Creating {plot_type} plot...", total=None)
        output_file = visualizer.create_plot(
            plot_type, data, output_file=output, **kwargs
        )

    # Success message
    file_size = os.path.getsize(output)
    console.print(
        f"[green]{plot_type.replace('_', ' ').title()} plot created successfully: [bold green]{output}[/bold green]"
    )
    if verbose:
        console.print(f"[green]File size: {file_size:,} bytes[/green]")

    return output_file


def _generate_sample_data(
    daily_data: bool,
    day: str,
    points_per_hour: int,
    data_hours: int,
    data_points: int,
    verbose: bool,
) -> pd.DataFrame:
    """
    Generate sample data with progress indicator

    Args:
        daily_data: Whether to generate daily data
        day: Day for daily data
        points_per_hour: Points per hour for daily data
        data_hours: Hours of data to generate
        data_points: Number of data points
        verbose: Whether to show verbose output

    Returns:
        Generated DataFrame
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=not verbose,
    ) as progress:
        if daily_data:
            task = progress.add_task(f"Generating daily data for {day}...", total=None)
            data = data_generator.generate_daily_plot_data(day)
        else:
            task = progress.add_task(
                f"Generating {data_points} data points...", total=None
            )
            data = data_generator.generate_plot_test_data(
                duration_hours=data_hours, 
                points_per_hour=data_points//data_hours if data_hours > 0 else 60,
                region="australia"
            )

    return data


def parse_time_range(time_str: str) -> Optional[Tuple[datetime, datetime]]:
    """Parse time range string in format 'start_time,end_time'"""
    if not time_str:
        return None

    try:
        start_str, end_str = time_str.split(",")
        start_time = datetime.fromisoformat(start_str.strip())
        end_time = datetime.fromisoformat(end_str.strip())
        return (start_time, end_time)
    except Exception as e:
        raise typer.BadParameter(
            f"Invalid time range format: {time_str}. Use 'YYYY-MM-DD HH:MM:SS,YYYY-MM-DD HH:MM:SS'"
        )


def parse_depth_range(depth_str: str) -> Optional[Tuple[float, float]]:
    """Parse depth range string in format 'min_depth,max_depth'"""
    if not depth_str:
        return None

    try:
        min_depth, max_depth = depth_str.split(",")
        return (float(min_depth.strip()), float(max_depth.strip()))
    except Exception as e:
        raise typer.BadParameter(
            f"Invalid depth range format: {depth_str}. Use 'min_depth,max_depth'"
        )


@app.command()
def time_series(
    # Data source options
    data_source: str = typer.Option(
        "Mixed (Historical + Real-time)", "--data-source", help="Data source type"
    ),
    # Variable selection
    variables: Optional[List[str]] = typer.Option(
        None, "--variables", "--vars", help="Comma-separated list of variables to plot"
    ),
    # Time range filtering
    time_range: Optional[str] = typer.Option(
        None,
        "--time-range",
        "--time",
        help="Time range in format 'start_time,end_time'",
    ),
    # Depth range filtering
    depth_range: Optional[str] = typer.Option(
        None,
        "--depth-range",
        "--depth",
        help="Depth range in format 'min_depth,max_depth'",
    ),
    # Real-time options
    real_time: bool = typer.Option(
        False, "--real-time", "--rt", help="Enable real-time update mode"
    ),
    status: str = typer.Option("Running", "--status", help="Real-time status"),
    # Display options
    annotations: bool = typer.Option(
        False, "--annotations", "--ann", help="Add annotations to the plot"
    ),
    statistics: bool = typer.Option(
        False, "--statistics", "--stats", help="Show statistical annotations"
    ),
    # Theme and styling
    theme: str = typer.Option("oceanographic", "--theme", help="Plot theme"),
    width: int = typer.Option(1000, "--width", help="Plot width in pixels"),
    height: int = typer.Option(700, "--height", help="Plot height in pixels"),
    # Data generation options
    data_hours: int = typer.Option(
        2, "--data-hours", help="Hours of sample data to generate"
    ),
    data_points: int = typer.Option(
        120, "--data-points", help="Number of data points to generate"
    ),
    daily_data: bool = typer.Option(
        False, "--daily-data", help="Generate data for a full day (24 hours)"
    ),
    day: str = typer.Option(
        "2024-01-01", "--day", help="Specific day for daily data (format: YYYY-MM-DD)"
    ),
    points_per_hour: int = typer.Option(
        10, "--points-per-hour", help="Data points per hour for daily data"
    ),
    # Output options
    output: str = typer.Option(
        "time_series_plot.html", "--output", "-o", help="Output HTML file path"
    ),
    title: Optional[str] = typer.Option(None, "--title", help="Custom plot title"),
    # Utility options
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Generate TRIAXUS time series plots with various parameters"""

    if verbose:
        console.print(
            Panel.fit("TRIAXUS Time Series Plot Generator", style="bold blue")
        )

    try:
        # Parse parameters
        parsed_variables = variables
        parsed_time_range = parse_time_range(time_range) if time_range else None
        parsed_depth_range = parse_depth_range(depth_range) if depth_range else None

        # Generate sample data
        data = _generate_sample_data(
            daily_data, day, points_per_hour, data_hours, data_points, verbose
        )

        if verbose:
            console.print(f"[green]Data generated: {len(data)} rows[/green]")
            console.print(f"[green]Available columns: {list(data.columns)}[/green]")
            console.print(
                f"[green]Variables: {parsed_variables or 'All standard variables'}[/green]"
            )
            console.print(f"[green]Time range: {parsed_time_range or 'All data'}[/green]")
            console.print(f"[green]Depth range: {parsed_depth_range or 'All depths'}[/green]")
            console.print(f"[green]Real-time: {real_time}[/green]")
            console.print(f"[green]Status: {status if real_time else 'N/A'}[/green]")

        # Prepare plot parameters
        plot_kwargs = {
            "data_source": data_source,
            "add_annotations": annotations,
            "show_statistics": statistics,
            "height": height,
            "width": width,
            "theme": theme,
        }

        if parsed_variables:
            plot_kwargs["selected_variables"] = parsed_variables

        if parsed_time_range:
            plot_kwargs["time_range"] = parsed_time_range

        if parsed_depth_range:
            plot_kwargs["depth_range"] = parsed_depth_range

        if real_time:
            plot_kwargs["real_time_update"] = True
            plot_kwargs["realtime_status"] = status

        if title:
            plot_kwargs["title"] = title

        # Create plot
        _create_plot_with_progress(
            "time_series", data, output, verbose, title, **plot_kwargs
        )

    except Exception as e:
        console.print(f"Error: [bold red]{e}[/bold red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def contour(
    # Data source options
    data_source: str = typer.Option(
        "Mixed (Historical + Real-time)", "--data-source", help="Data source type"
    ),
    # Variable selection
    variable: str = typer.Option(
        "temperature", "--variable", help="Variable for contour plot"
    ),
    # Time range filtering
    time_range: Optional[str] = typer.Option(
        None,
        "--time-range",
        "--time",
        help="Time range in format 'start_time,end_time'",
    ),
    # Depth range filtering
    depth_range: Optional[str] = typer.Option(
        None,
        "--depth-range",
        "--depth",
        help="Depth range in format 'min_depth,max_depth'",
    ),
    # Display options
    annotations: bool = typer.Option(
        False, "--annotations", "--ann", help="Add annotations to the plot"
    ),
    # Theme and styling
    theme: str = typer.Option("oceanographic", "--theme", help="Plot theme"),
    width: int = typer.Option(1000, "--width", help="Plot width in pixels"),
    height: int = typer.Option(700, "--height", help="Plot height in pixels"),
    # Data generation options
    data_hours: int = typer.Option(
        2, "--data-hours", help="Hours of sample data to generate"
    ),
    data_points: int = typer.Option(
        120, "--data-points", help="Number of data points to generate"
    ),
    daily_data: bool = typer.Option(
        False, "--daily-data", help="Generate data for a full day (24 hours)"
    ),
    day: str = typer.Option(
        "2024-01-01", "--day", help="Specific day for daily data (format: YYYY-MM-DD)"
    ),
    points_per_hour: int = typer.Option(
        10, "--points-per-hour", help="Data points per hour for daily data"
    ),
    # Output options
    output: str = typer.Option(
        "contour_plot.html", "--output", "-o", help="Output HTML file path"
    ),
    title: Optional[str] = typer.Option(None, "--title", help="Custom plot title"),
    # Utility options
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Generate TRIAXUS contour plots with various parameters"""

    if verbose:
        console.print(Panel.fit("TRIAXUS Contour Plot Generator", style="bold blue"))

    try:
        # Parse parameters
        parsed_time_range = parse_time_range(time_range) if time_range else None
        parsed_depth_range = parse_depth_range(depth_range) if depth_range else None

        # Create sample data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            if daily_data:
                task = progress.add_task(
                    f"Generating daily data for {day}...", total=None
                )
                data = data_generator.generate_daily_plot_data(day)
            else:
                task = progress.add_task(
                    f"Generating {data_points} data points...", total=None
                )
                data = data_generator.generate_plot_test_data(
                duration_hours=data_hours, 
                points_per_hour=data_points//data_hours if data_hours > 0 else 60,
                region="australia"
            )

        if verbose:
            console.print(f"[green]Data generated: {len(data)} rows[/green]")
            console.print(f"[green]Contour variable: {variable}[/green]")
            console.print(f"[green]Time range: {parsed_time_range or 'All data'}[/green]")
            console.print(f"[green]Depth range: {parsed_depth_range or 'All depths'}[/green]")

        # Initialize visualizer
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task(
                f"Initializing visualizer with theme: {theme}...", total=None
            )
            visualizer = TriaxusVisualizer(theme=theme)

        # Prepare plot parameters
        plot_kwargs = {
            "data_source": data_source,
            "add_annotations": annotations,
            "height": height,
            "width": width,
        }

        if parsed_time_range:
            plot_kwargs["time_range"] = parsed_time_range

        if parsed_depth_range:
            plot_kwargs["depth_range"] = parsed_depth_range

        if title:
            plot_kwargs["title"] = title

        # Create plot
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task("Creating contour plot...", total=None)
            output_file = visualizer.create_plot(
                "contour", data, output_file=output, variable=variable, **plot_kwargs
            )

        # Plot already saved by create_plot method

        # Success message
        file_size = os.path.getsize(output)
        console.print(
            f"[green]Contour plot created successfully: [bold green]{output}[/bold green]"
        )
        if verbose:
            console.print(f"[green]File size: {file_size:,} bytes[/green]")

    except Exception as e:
        console.print(f"Error: [bold red]{e}[/bold red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def map(
    # Data source options
    data_source: str = typer.Option(
        "Mixed (Historical + Real-time)", "--data-source", help="Data source type"
    ),
    # Time range filtering
    time_range: Optional[str] = typer.Option(
        None,
        "--time-range",
        "--time",
        help="Time range in format 'start_time,end_time'",
    ),
    # Display options
    annotations: bool = typer.Option(
        False, "--annotations", "--ann", help="Add annotations to the plot"
    ),
    # Theme and styling
    theme: str = typer.Option("oceanographic", "--theme", help="Plot theme"),
    # Map style options
    map_style: str = typer.Option(
        "satellite-streets",
        "--map-style",
        help="Map style: satellite-streets, satellite, streets, outdoors, light, dark, basic, hybrid",
    ),
    width: int = typer.Option(1000, "--width", help="Plot width in pixels"),
    height: int = typer.Option(700, "--height", help="Plot height in pixels"),
    # Data generation options
    data_hours: int = typer.Option(
        2, "--data-hours", help="Hours of sample data to generate"
    ),
    data_points: int = typer.Option(
        120, "--data-points", help="Number of data points to generate"
    ),
    daily_data: bool = typer.Option(
        False, "--daily-data", help="Generate data for a full day (24 hours)"
    ),
    day: str = typer.Option(
        "2024-01-01", "--day", help="Specific day for daily data (format: YYYY-MM-DD)"
    ),
    points_per_hour: int = typer.Option(
        10, "--points-per-hour", help="Data points per hour for daily data"
    ),
    # Output options
    output: str = typer.Option(
        "map_plot.html", "--output", "-o", help="Output HTML file path"
    ),
    title: Optional[str] = typer.Option(None, "--title", help="Custom plot title"),
    # Utility options
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Generate TRIAXUS map plots with various parameters"""

    if verbose:
        console.print(Panel.fit("TRIAXUS Map Plot Generator", style="bold blue"))

    try:
        # Parse parameters
        parsed_time_range = parse_time_range(time_range) if time_range else None

        # Create sample data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            if daily_data:
                task = progress.add_task(
                    f"Generating daily map data for {day}...", total=None
                )
                # For daily data, generate map trajectory data
                from datetime import datetime
                start_time = datetime.strptime(day, "%Y-%m-%d")
                data = data_generator.generate_map_trajectory_data(
                    duration_hours=24.0, 
                    points_per_hour=data_points//24 if data_points > 24 else 10,
                    start_time=start_time
                )
            else:
                task = progress.add_task(
                    f"Generating {data_points} map trajectory points...", total=None
                )
                # Use map trajectory data generator for map plots
                data = data_generator.generate_map_trajectory_data(
                    duration_hours=data_hours, 
                    points_per_hour=data_points//data_hours if data_hours > 0 else 60
                )

        if verbose:
            console.print(f"[green]Data generated: {len(data)} rows[/green]")
            console.print(f"[green]Time range: {parsed_time_range or 'All data'}[/green]")

        # Initialize visualizer
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task(
                f"Initializing visualizer with theme: {theme}...", total=None
            )
            visualizer = TriaxusVisualizer(theme=theme)

        # Prepare plot parameters
        plot_kwargs = {
            "data_source": data_source,
            "add_annotations": annotations,
            "height": height,
            "width": width,
            "map_style": map_style,
        }

        if parsed_time_range:
            plot_kwargs["time_range"] = parsed_time_range

        if title:
            plot_kwargs["title"] = title

        # Create plot
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task("Creating map plot...", total=None)
            output_file = visualizer.create_plot(
                "map", data, output_file=output, **plot_kwargs
            )

        # Plot already saved by create_plot method

        # Success message
        file_size = os.path.getsize(output)
        console.print(
            f"[green]Map plot created successfully: [bold green]{output}[/bold green]"
        )
        if verbose:
            console.print(f"[green]File size: {file_size:,} bytes[/green]")

    except Exception as e:
        console.print(f"Error: [bold red]{e}[/bold red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def depth_profile(
    output: str = typer.Option(
        "depth_profile.html", "--output", "-o", help="Output HTML file path"
    ),
    variables: str = typer.Option(
        "tv290c", "--variables", help="Variables to plot (comma-separated)"
    ),
    depth_range: str = typer.Option(
        None, "--depth-range", help="Depth range filter (format: 'min,max')"
    ),
    add_depth_zones: bool = typer.Option(
        False, "--depth-zones", help="Add ocean depth zones"
    ),
    thermocline: bool = typer.Option(
        False, "--thermocline", help="Add thermocline detection"
    ),
    theme: str = typer.Option("oceanographic", "--theme", help="Theme for the plot"),
    width: int = typer.Option(800, "--width", help="Plot width in pixels"),
    height: int = typer.Option(600, "--height", help="Plot height in pixels"),
    title: str = typer.Option(None, "--title", help="Custom title for the plot"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Create a depth profile plot showing variables vs depth"""
    try:
        if verbose:
            console.print("Creating depth profile plot...", style="blue")

        # Parse variables - data generator already uses correct column names
        variable_list = [v.strip() for v in variables.split(",")]
        mapped_variables = variable_list  # No mapping needed, use as-is

        # Generate sample data
        data = data_generator.generate_plot_test_data()

        # Create visualizer
        visualizer = TriaxusVisualizer(theme=theme)

        # Create plot
        output_file = visualizer.create_plot(
            "depth_profile",
            data,
            output_file=output,
            **{
                "variables": mapped_variables,
                "add_depth_zones": add_depth_zones,
                "width": width,
                "height": height,
                "title": title,
            },
        )

        # Plot already saved by create_plot method

        if verbose:
            console.print(f"Depth profile plot saved to: {output}", style="green")
        else:
            console.print(f"Depth profile plot created: {output}")

    except Exception as e:
        console.print(f"Error creating depth profile plot: {e}", style="red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def list_variables():
    """List available standard variables"""
    table = Table(title="Standard TRIAXUS Variables")
    table.add_column("Variable", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    variables = [
        ("temperature", "Temperature measurements"),
        ("salinity", "Salinity measurements"),
        ("oxygen", "Dissolved oxygen measurements"),
        ("fluorescence", "Fluorescence measurements"),
        ("ph", "pH measurements"),
    ]

    for var, desc in variables:
        table.add_row(var, desc)

    console.print(table)
    console.print("\n[bold]Usage:[/bold] --variables temperature,salinity,oxygen")


@app.command()
def themes():
    """List available themes"""
    table = Table(title="Available Themes")
    table.add_column("Theme", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    themes_list = [
        ("oceanographic", "Oceanographic theme (default)"),
        ("dark", "Dark theme"),
        ("default", "Default theme"),
        ("high_contrast", "High contrast theme"),
    ]

    for theme, desc in themes_list:
        table.add_row(theme, desc)

    console.print(table)
    console.print("\n[bold]Usage:[/bold] --theme dark")


@app.command()
def data_info():
    """Show information about plot test data generation"""
    table = Table(title="Plot Test Data Generation Information")
    table.add_column("Feature", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    features = [
        ("Purpose", "Generate test data for plot functionality testing"),
        ("Variables", "temperature, salinity, oxygen, fluorescence, ph"),
        ("Time Options", "Custom hours, full day (24h), quick test"),
        ("Realistic Data", "Oceanographic patterns with natural variation"),
        ("GPS Coordinates", "Simulated cruise tracks (regional oceanographic data)"),
        ("Reproducible", "Fixed random seed for consistent results"),
        ("Plot Focused", "Designed specifically for testing plot functionality"),
        (
            "Convenience Functions",
            "generate_plot_test_data(), generate_daily_plot_data(), generate_quick_plot_data()",
        ),
    ]

    for feature, desc in features:
        table.add_row(feature, desc)

    console.print(table)

    # Show plot test usage examples
    console.print(f"\n[bold]Plot Test Usage Examples:[/bold]")
    console.print(
        "  from triaxus.data.simple_data_generator import PlotTestDataGenerator"
    )
    console.print("  generator = PlotTestDataGenerator()")
    console.print(
        "  data = generator.generate_plot_test_data(hours=2.0)  # 2 hours of plot test data"
    )
    console.print(
        "  daily = generator.generate_daily_plot_data('2024-01-01')  # Full day plot test data"
    )
    console.print(
        "  quick = generator.generate_quick_plot_data()  # Quick plot test data"
    )

    # Show variable information
    console.print(f"\n[bold]Generated Variables:[/bold]")
    variables = [
        ("time", "Time series"),
        ("depth", "Depth in meters"),
        ("latitude", "GPS latitude"),
        ("longitude", "GPS longitude"),
        ("tv290c", "Temperature (°C)"),
        ("sal00", "Salinity (PSU)"),
        ("sbeox0mm_l", "Oxygen (mg/L)"),
        ("fleco_afl", "Fluorescence (RFU)"),
        ("ph", "pH value"),
    ]
    for var, desc in variables:
        console.print(f"  {var}: {desc}")


@app.command()
def examples():
    """Show usage examples"""
    examples_text = """
[bold blue]Time Series Plot Examples:[/bold blue]

[cyan]1. Basic time series plot:[/cyan]
   triaxus-plot time-series --output basic.html

[cyan]2. Time series with specific variables:[/cyan]
   triaxus-plot time-series --variables temperature,salinity,oxygen --output temp_sal_oxy.html

[cyan]3. Time series with time range filtering:[/cyan]
   triaxus-plot time-series --time-range "2024-01-01 10:00:00,2024-01-01 12:00:00" --output filtered_time.html

[cyan]4. Real-time time series plot:[/cyan]
   triaxus-plot time-series --real-time --status Running --output realtime.html

[bold blue]Contour Plot Examples:[/bold blue]

[cyan]5. Basic contour plot:[/cyan]
   triaxus-plot contour --variable temperature --output contour_temp.html

[cyan]6. Contour plot with depth range:[/cyan]
   triaxus-plot contour --variable salinity --depth-range "20,80" --output contour_sal.html

[cyan]7. Daily contour plot:[/cyan]
   triaxus-plot contour --daily-data --day "2024-01-01" --variable oxygen --output daily_contour.html

[bold blue]Map Plot Examples:[/bold blue]

[cyan]8. Basic map plot:[/cyan]
   triaxus-plot map --output map_basic.html

[cyan]9. Map plot with time range:[/cyan]
   triaxus-plot map --time-range "2024-01-01 08:00:00,2024-01-01 18:00:00" --output map_filtered.html

[cyan]10. Daily map plot:[/cyan]
    triaxus-plot map --daily-data --day "2024-01-01" --output daily_map.html

[bold blue]Advanced Examples:[/bold blue]

[cyan]11. Industry standard time series:[/cyan]
    triaxus-plot time-series \\
      --data-source "Mixed (Historical + Real-time)" \\
      --variables temperature,salinity,oxygen,fluorescence,ph \\
      --time-range "2024-01-01 10:00:00,2024-01-01 12:00:00" \\
      --depth-range "10,100" \\
      --real-time \\
      --status Running \\
      --annotations \\
      --statistics \\
      --output industry_standard.html

[cyan]12. Custom theme and size:[/cyan]
    triaxus-plot time-series --theme dark --width 1200 --height 800 --output custom_theme.html
    """

    console.print(
        Panel(examples_text, title="TRIAXUS Plot Examples", border_style="blue")
    )


if __name__ == "__main__":
    app()
