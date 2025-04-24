import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


class AcidSitesAnalyzer:
    def __init__(self, csv_path="acid_sites.csv", extract_data=False):
        """Initialize the analyzer with the path to the CSV file.

        Args:
            csv_path (str): Path to the CSV file containing acid sites data
            extract_data (bool): If True, extract data from PyrIR folders before loading CSV
        """
        self.csv_path = csv_path
        if extract_data:
            self.extract_acid_sites()
        self.df = pd.read_csv(csv_path)
        self._setup_plot_style()

    def _setup_plot_style(self):
        """Set up consistent plot styling."""
        plt.style.use("seaborn")
        plt.rcParams["font.size"] = 12
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 14
        plt.rcParams["xtick.labelsize"] = 10
        plt.rcParams["ytick.labelsize"] = 10
        plt.rcParams["legend.fontsize"] = 10

    def get_acid_sites_from_measurement(self, measurement):
        """Extract acid sites data from a measurement, handling both list and dict formats.

        The method handles both old and new JSON formats:
        - Old format: number_acid_sites and site_density as top-level keys
        - New format: all acid site data nested under number_acid_sites
        """
        # Try new format first
        acid_sites = measurement.get("number_acid_sites", {})
        if acid_sites and isinstance(acid_sites, dict):
            # Extract from new format
            bronsted_mmol = (
                acid_sites.get("bronsted", {}).get("concentration", {}).get("value")
            )
            lewis_mmol = (
                acid_sites.get("lewis", {}).get("concentration", {}).get("value")
            )
            bronsted_nm2 = (
                acid_sites.get("bronsted", {}).get("surface_density", {}).get("value")
            )
            lewis_nm2 = (
                acid_sites.get("lewis", {}).get("surface_density", {}).get("value")
            )
            bronsted_umol_nm2 = (
                acid_sites.get("bronsted", {})
                .get("surface_concentration", {})
                .get("value")
            )
            lewis_umol_nm2 = (
                acid_sites.get("lewis", {})
                .get("surface_concentration", {})
                .get("value")
            )

            # Extract errors
            bronsted_mmol_err = (
                acid_sites.get("bronsted", {}).get("concentration", {}).get("error")
            )
            lewis_mmol_err = (
                acid_sites.get("lewis", {}).get("concentration", {}).get("error")
            )
            bronsted_nm2_err = (
                acid_sites.get("bronsted", {}).get("surface_density", {}).get("error")
            )
            lewis_nm2_err = (
                acid_sites.get("lewis", {}).get("surface_density", {}).get("error")
            )
            bronsted_umol_nm2_err = (
                acid_sites.get("bronsted", {})
                .get("surface_concentration", {})
                .get("error")
            )
            lewis_umol_nm2_err = (
                acid_sites.get("lewis", {})
                .get("surface_concentration", {})
                .get("error")
            )

            return (
                bronsted_mmol,
                lewis_mmol,
                bronsted_nm2,
                lewis_nm2,
                bronsted_umol_nm2,
                lewis_umol_nm2,
                bronsted_mmol_err,
                lewis_mmol_err,
                bronsted_nm2_err,
                lewis_nm2_err,
                bronsted_umol_nm2_err,
                lewis_umol_nm2_err,
            )

        # Fall back to old format
        number_acid_sites = measurement.get("number_acid_sites", {})
        site_density = measurement.get("site_density", {})
        surface_concentration = measurement.get("surface_concentration", {})

        # If number_acid_sites is a list, it means no data is available
        if isinstance(number_acid_sites, list):
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            )

        # Extract values if available
        bronsted_mmol = (
            number_acid_sites.get("bronsted", {}).get("value")
            if isinstance(number_acid_sites, dict)
            else None
        )
        lewis_mmol = (
            number_acid_sites.get("lewis", {}).get("value")
            if isinstance(number_acid_sites, dict)
            else None
        )

        # Handle site density similarly
        if isinstance(site_density, dict):
            bronsted_nm2 = (
                site_density.get("bronsted", {}).get("value")
                if site_density.get("bronsted")
                else None
            )
            lewis_nm2 = (
                site_density.get("lewis", {}).get("value")
                if site_density.get("lewis")
                else None
            )
        else:
            bronsted_nm2 = None
            lewis_nm2 = None

        # Handle surface concentration
        if isinstance(surface_concentration, dict):
            bronsted_umol_nm2 = (
                surface_concentration.get("bronsted", {}).get("value")
                if surface_concentration.get("bronsted")
                else None
            )
            lewis_umol_nm2 = (
                surface_concentration.get("lewis", {}).get("value")
                if surface_concentration.get("lewis")
                else None
            )
        else:
            bronsted_umol_nm2 = None
            lewis_umol_nm2 = None

        # For old format, set errors to None
        bronsted_mmol_err = None
        lewis_mmol_err = None
        bronsted_nm2_err = None
        lewis_nm2_err = None
        bronsted_umol_nm2_err = None
        lewis_umol_nm2_err = None

        return (
            bronsted_mmol,
            lewis_mmol,
            bronsted_nm2,
            lewis_nm2,
            bronsted_umol_nm2,
            lewis_umol_nm2,
            bronsted_mmol_err,
            lewis_mmol_err,
            bronsted_nm2_err,
            lewis_nm2_err,
            bronsted_umol_nm2_err,
            lewis_umol_nm2_err,
        )

    def extract_acid_sites(self):
        """Extract acid sites data from PyrIR folders and save to CSV."""
        # Find all PyrIR folders
        pyrir_folders = [
            f for f in os.listdir(".") if f.startswith("PyrIR") and os.path.isdir(f)
        ]

        # Initialize data structure
        data = {}

        for folder in pyrir_folders:
            try:
                # Get sample name from folder name
                sample_name = folder.replace("PyrIR_", "")

                # Path to JSON file
                json_path = os.path.join(folder, "fits_plots", f"{folder}.json")

                if not os.path.exists(json_path):
                    print(f"Warning: JSON file not found for {folder}")
                    continue

                # Read JSON file
                with open(json_path, "r") as f:
                    json_data = json.load(f)

                # Initialize sample data
                if sample_name not in data:
                    data[sample_name] = {
                        "sample": [],
                        "temperature": [],
                        "bronsted_mmol_g": [],
                        "lewis_mmol_g": [],
                        "bronsted_nm2": [],
                        "lewis_nm2": [],
                        "bronsted_umol_nm2": [],
                        "lewis_umol_nm2": [],
                        "bronsted_mmol_g_err": [],
                        "lewis_mmol_g_err": [],
                        "bronsted_nm2_err": [],
                        "lewis_nm2_err": [],
                        "bronsted_umol_nm2_err": [],
                        "lewis_umol_nm2_err": [],
                    }

                # Extract data from measurements
                for measurement in json_data.get("measurements", []):
                    try:
                        temp = measurement.get("temperature")
                        (
                            bronsted_mmol,
                            lewis_mmol,
                            bronsted_nm2,
                            lewis_nm2,
                            bronsted_umol_nm2,
                            lewis_umol_nm2,
                            bronsted_mmol_err,
                            lewis_mmol_err,
                            bronsted_nm2_err,
                            lewis_nm2_err,
                            bronsted_umol_nm2_err,
                            lewis_umol_nm2_err,
                        ) = self.get_acid_sites_from_measurement(measurement)

                        # Only add data if temperature and at least one acid site value is present
                        if temp is not None and any(
                            v is not None for v in [bronsted_mmol, lewis_mmol]
                        ):
                            data[sample_name]["sample"].append(sample_name)
                            data[sample_name]["temperature"].append(temp)
                            data[sample_name]["bronsted_mmol_g"].append(bronsted_mmol)
                            data[sample_name]["lewis_mmol_g"].append(lewis_mmol)
                            data[sample_name]["bronsted_nm2"].append(bronsted_nm2)
                            data[sample_name]["lewis_nm2"].append(lewis_nm2)
                            # Format surface concentration values in scientific notation
                            data[sample_name]["bronsted_umol_nm2"].append(
                                f"{bronsted_umol_nm2:.2e}"
                                if bronsted_umol_nm2 is not None
                                else None
                            )
                            data[sample_name]["lewis_umol_nm2"].append(
                                f"{lewis_umol_nm2:.2e}"
                                if lewis_umol_nm2 is not None
                                else None
                            )
                            data[sample_name]["bronsted_mmol_g_err"].append(
                                bronsted_mmol_err
                            )
                            data[sample_name]["lewis_mmol_g_err"].append(lewis_mmol_err)
                            data[sample_name]["bronsted_nm2_err"].append(
                                bronsted_nm2_err
                            )
                            data[sample_name]["lewis_nm2_err"].append(lewis_nm2_err)
                            # Format surface concentration error values in scientific notation
                            data[sample_name]["bronsted_umol_nm2_err"].append(
                                f"{bronsted_umol_nm2_err:.2e}"
                                if bronsted_umol_nm2_err is not None
                                else None
                            )
                            data[sample_name]["lewis_umol_nm2_err"].append(
                                f"{lewis_umol_nm2_err:.2e}"
                                if lewis_umol_nm2_err is not None
                                else None
                            )
                    except Exception as e:
                        print(
                            f"Warning: Error processing measurement in {folder}: {str(e)}"
                        )
                        continue
            except Exception as e:
                print(f"Error processing folder {folder}: {str(e)}")
                continue

        if not data:
            print("No data was found in any of the PyrIR folders")
            return

        # Create DataFrame and save to CSV
        all_data = []
        for sample, sample_data in data.items():
            if any(len(v) > 0 for v in sample_data.values()):
                # Create a temporary DataFrame for this sample
                temp_df = pd.DataFrame(sample_data)
                # Add a unique identifier for each row
                temp_df["id"] = range(len(temp_df))
                all_data.append(temp_df)

        if not all_data:
            print("No valid data to save")
            return

        # Concatenate all DataFrames
        final_df = pd.concat(all_data, ignore_index=True)

        # Sort by sample and temperature
        final_df = final_df.sort_values(["sample", "temperature"])

        # Round numeric columns to 6 decimal places (except surface concentration columns)
        numeric_columns = [
            "bronsted_mmol_g",
            "lewis_mmol_g",
            "bronsted_nm2",
            "lewis_nm2",
            "bronsted_mmol_g_err",
            "lewis_mmol_g_err",
            "bronsted_nm2_err",
            "lewis_nm2_err",
        ]
        final_df[numeric_columns] = final_df[numeric_columns].round(6)

        # Reorder columns to put sample first
        columns = [
            "sample",
            "temperature",
            "bronsted_mmol_g",
            "lewis_mmol_g",
            "bronsted_nm2",
            "lewis_nm2",
            "bronsted_umol_nm2",
            "lewis_umol_nm2",
            "bronsted_mmol_g_err",
            "lewis_mmol_g_err",
            "bronsted_nm2_err",
            "lewis_nm2_err",
            "bronsted_umol_nm2_err",
            "lewis_umol_nm2_err",
        ]
        final_df = final_df[columns]

        # Save to CSV
        final_df.to_csv(self.csv_path, index=False)
        print("Data successfully saved to", self.csv_path)
        print(
            f"Processed {len(pyrir_folders)} folders and found data for {len(data)} samples"
        )

    def get_available_samples(self):
        """Return a list of available sample names."""
        return sorted(self.df["sample"].unique())

    def get_available_temperatures(self):
        """Return a list of available temperatures."""
        return sorted(self.df["temperature"].unique())

    def plot_acid_sites_vs_temp(
        self, sample_index, option="concentration", save_path=None, show=True
    ):
        """Plot Lewis and Bronsted acid sites for one sample over temperature.

        Args:
            sample_index (int): Index of the sample in the list of available samples
            option (str, optional): Calculation option to plot, either "concentration", "surface_density", or "surface_concentration".
                                  Defaults to "concentration".
            save_path (str, optional): Path to save the plot. If None, saves as "{sample_name}_T_{option}.png"
            show (bool, optional): Whether to display the plot. Defaults to True.
        """
        # Get sample name from index
        all_samples = sorted(self.df["sample"].unique())
        sample_name = all_samples[sample_index]

        # Filter data for the specified sample
        sample_data = self.df[self.df["sample"] == sample_name]

        if sample_data.empty:
            print(f"No data found for sample {sample_name}")
            return

        # Create figure with two y-axes
        fig = plt.figure(figsize=(8, 6), facecolor="white")
        ax1 = fig.add_subplot(facecolor="white")
        ax2 = ax1.twinx()

        # Remove grid
        ax1.grid(False)
        ax2.grid(False)

        # Plot Lewis acid sites
        ax1.plot(
            sample_data["temperature"],
            (
                sample_data["lewis_mmol_g"]
                if option == "concentration"
                else sample_data["lewis_nm2"]
            ),
            color="black",
            marker="o",
            linestyle="None",
            label="Lewis",
            fillstyle="full",
        )

        # Plot Bronsted acid sites
        ax2.plot(
            sample_data["temperature"],
            (
                sample_data["bronsted_mmol_g"]
                if option == "concentration"
                else sample_data["bronsted_nm2"]
            ),
            color="dimgrey",
            marker="o",
            linestyle="None",
            label="Bronsted",
            fillstyle="none",
            markeredgewidth=1.5,
        )

        # Set labels and limits
        ax1.set_xlabel("$T_{Des}$ / °C")
        if option == "concentration":
            ax1.set_ylabel("$n_{LAS}$ / μmol g$^{-1}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / μmol g$^{-1}$" + " ○", color="dimgrey")
        elif option == "surface_density":
            ax1.set_ylabel("$n_{LAS}$ / nm$^{-2}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / nm$^{-2}$" + " ○", color="dimgrey")
        else:  # surface_concentration
            ax1.set_ylabel("$n_{LAS}$ / μmol nm$^{-2}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / μmol nm$^{-2}$" + " ○", color="dimgrey")

        # Set axis colors, linewidths, and ticks
        for spine in ax1.spines.values():
            spine.set_color("black")
            spine.set_linewidth(1)
        for spine in ax2.spines.values():
            spine.set_color("dimgrey")
            spine.set_linewidth(1)

        # Configure ticks for both axes
        ax1.tick_params(
            axis="both",
            which="both",
            direction="out",
            length=6,
            width=1,
            colors="black",
            bottom=True,
            top=False,
            left=True,
            right=False,
        )

        ax2.tick_params(
            axis="y",
            which="both",
            direction="out",
            length=6,
            width=1,
            colors="dimgrey",
            left=False,
            right=True,
        )

        # Adjust layout
        plt.tight_layout()

        # Save plot with transparent background
        if save_path:
            plt.savefig(save_path, dpi=600, transparent=True, bbox_inches="tight")
        else:
            plt.savefig(
                f"{sample_name}_T_{option}.png",
                dpi=600,
                transparent=True,
                bbox_inches="tight",
            )

        # Show plot if requested
        if show:
            plt.show()
        else:
            plt.close()

        return fig

    def plot_acid_sites_at_temp(
        self,
        temperature,
        sample_indices=None,
        save_path=None,
        option="concentration",
        colors=None,
    ):
        """Plot Lewis and Bronsted acid sites for specified samples at a given temperature.

        Args:
            temperature (int): Temperature in °C
            sample_indices (list, optional): List of sample indices to plot. If None, all samples are plotted.
            save_path (str, optional): Path to save the plot
            option (str, optional): Calculation option to plot, either "concentration", "surface_density", or "surface_concentration".
                                  Defaults to "concentration".
            colors (list, optional): List of colors to use for the samples. If None, uses default colors.
        """
        # Filter data for the specified temperature
        temp_data = self.df[self.df["temperature"] == temperature]

        if temp_data.empty:
            print(f"No data found for temperature {temperature}°C")
            return

        # If sample_indices is provided, filter for those samples
        if sample_indices is not None:
            all_samples = sorted(temp_data["sample"].unique())
            selected_samples = [all_samples[i] for i in sample_indices]

            # Check if all samples have the same OMAS_1-x pattern
            omas_patterns = set()
            temp_patterns = set()
            for sample in selected_samples:
                parts = sample.split("_")
                # Get OMAS_1-x pattern (first two parts)
                omas_pattern = "_".join(parts[:2])  # OMAS_1-x
                # Get temperature pattern (Txx) ignoring any suffixes
                temp_part = next((p for p in parts if p.startswith("T")), "")
                temp_pattern = temp_part.split("_")[0]  # Take only Txx part
                omas_patterns.add(omas_pattern)
                temp_patterns.add(temp_pattern)

            # Format sample names based on pattern changes
            formatted_samples = []
            xlabel = "Sample"  # Default xlabel
            for sample in selected_samples:
                parts = sample.split("_")
                if len(omas_patterns) == 1 and len(temp_patterns) > 1:
                    # Only temperature changes, show Txx
                    temp_part = next((p for p in parts if p.startswith("T")), "")
                    formatted_samples.append(temp_part.split("_")[0])
                    # Get the metal concentration (1/x) from the sample name
                    ratio = parts[1].split("1-")[1]
                    xlabel = f"OMAS 1/{ratio}"
                elif len(omas_patterns) > 1 and len(temp_patterns) == 1:
                    # Only OMAS_1-x changes, show 1/x
                    ratio = parts[1].split("1-")[1]
                    formatted_samples.append(f"1/{ratio}")
                    xlabel = "OMAS 1/x"
                else:
                    # Both change or neither changes, show full name
                    formatted_samples.append(sample)
                    xlabel = "Sample"

            # Create a new DataFrame with only the selected samples in the correct order
            temp_data = pd.DataFrame()
            for sample in selected_samples:
                sample_data = self.df[
                    (self.df["sample"] == sample)
                    & (self.df["temperature"] == temperature)
                ]
                temp_data = pd.concat([temp_data, sample_data])
        else:
            formatted_samples = temp_data["sample"]
            xlabel = "Sample"

            # Sort by Al:Si ratio only if no specific order is given
            def get_al_si_ratio(sample_name):
                try:
                    parts = sample_name.split("_")
                    for part in parts:
                        if "1-" in part:
                            return int(part.split("1-")[1].split("_")[0])
                except:
                    return float("inf")
                return float("inf")

            temp_data = temp_data.sort_values(
                "sample", key=lambda x: x.map(get_al_si_ratio)
            )

        # Create figure with two y-axes
        fig = plt.figure(figsize=(10, 6), facecolor="none")
        ax1 = fig.add_subplot(facecolor="none")
        ax2 = ax1.twinx()

        # Remove grid
        ax1.grid(False)
        ax2.grid(False)

        # Define colors and markers
        if colors is None:
            colors = [
                "black",
                "blue",
                "red",
                "green",
                "orange",
                "purple",
                "brown",
                "pink",
            ]
        markers = ["o", "v", "s", "h", "*", "D", "P", "X"]

        # Plot data for each sample
        for i, (_, row) in enumerate(temp_data.iterrows()):
            # Plot Lewis acid sites
            ax1.plot(
                i,
                row["lewis_mmol_g"] if option == "concentration" else row["lewis_nm2"],
                color=colors[i % len(colors)],
                marker=markers[i % len(markers)],
                linestyle="None",
                label=formatted_samples[i],
                fillstyle="full",  # Explicitly set filled markers for Lewis
            )

            # Plot Bronsted acid sites
            ax2.plot(
                i,
                (
                    row["bronsted_mmol_g"]
                    if option == "concentration"
                    else row["bronsted_nm2"]
                ),
                color=colors[i % len(colors)],
                marker=markers[i % len(markers)],
                linestyle="None",
                label=None,
                fillstyle="none",  # Explicitly set hollow markers for Bronsted
                markeredgewidth=1.5,  # Make the edges slightly thicker for better visibility
            )

        # Set labels and limits
        ax1.set_xlabel(xlabel)

        # Add markers to axis labels with appropriate units
        if option == "concentration":
            ax1.set_ylabel("$n_{LAS}$ / μmol g$^{-1}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / μmol g$^{-1}$" + " ○", color="dimgrey")
        elif option == "surface_density":
            ax1.set_ylabel("$n_{LAS}$ / nm$^{-2}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / nm$^{-2}$" + " ○", color="dimgrey")
        else:  # surface_concentration
            ax1.set_ylabel("$n_{LAS}$ / μmol m$^{-2}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / μmol m$^{-2}$" + " ○", color="dimgrey")

        # Set y-axis limits separately for each axis
        # For Lewis acid sites (ax1)
        lewis_col = "lewis_mmol_g" if option == "concentration" else "lewis_nm2"
        lewis_min = temp_data[lewis_col].min()
        lewis_max = temp_data[lewis_col].max()
        lewis_padding = (lewis_max - lewis_min) * 0.2
        ax1.set_ylim(lewis_min - lewis_padding, lewis_max + lewis_padding)

        # For Bronsted acid sites (ax2)
        bronsted_col = (
            "bronsted_mmol_g" if option == "concentration" else "bronsted_nm2"
        )
        bronsted_min = temp_data[bronsted_col].min()
        bronsted_max = temp_data[bronsted_col].max()
        bronsted_padding = (bronsted_max - bronsted_min) * 0.2
        ax2.set_ylim(bronsted_min - bronsted_padding, bronsted_max + bronsted_padding)

        # Set x-axis ticks with formatted sample names
        ax1.set_xticks(range(len(temp_data)))
        ax1.set_xticklabels(formatted_samples, rotation=45, ha="right")

        # Set axis colors, linewidths, and ticks
        for spine in ax1.spines.values():
            spine.set_color("black")
            spine.set_linewidth(1)
        for spine in ax2.spines.values():
            spine.set_color("dimgrey")
            spine.set_linewidth(1)

        # Configure ticks for both axes
        ax1.tick_params(
            axis="both",
            which="both",
            direction="out",
            length=6,
            width=1,
            colors="black",
            bottom=True,
            top=False,
            left=True,
            right=False,
        )

        ax2.tick_params(
            axis="y",
            which="both",
            direction="out",
            length=6,
            width=1,
            colors="dimgrey",
            left=False,
            right=True,
        )

        # Adjust layout
        plt.tight_layout()

        # Save plot
        if save_path:
            plt.savefig(save_path, dpi=600, transparent=True, bbox_inches="tight")
        else:
            # Create save path with xlabel
            save_path = f"acid_sites_at_{temperature}C_{xlabel.replace(' ', '_').replace('/', '_')}.png"
            plt.savefig(save_path, dpi=600, transparent=True, bbox_inches="tight")

        return fig

    def plot_acid_sites_bar(
        self,
        sample_indices,
        acid_type="lewis",
        option="concentration",
        save_path=None,
        show=True,
        colors=None,
    ):
        """Plot bar chart of acid sites for selected samples across temperatures.

        Args:
            sample_indices (list): List of sample indices to plot
            acid_type (str, optional): Type of acid site to plot, either "lewis" or "bronsted". Defaults to "lewis".
            option (str, optional): Calculation option to plot, either "concentration", "surface_density", or "surface_concentration".
                                  Defaults to "concentration".
            save_path (str, optional): Path to save the plot. If None, saves as "acid_sites_bar_{acid_type}_{option}.png"
            show (bool, optional): Whether to display the plot. Defaults to True.
            colors (list, optional): List of colors to use for the samples. If None, uses default colors.
        """
        # Turn off interactive mode to prevent automatic display
        plt.ioff()

        # Get all available samples and temperatures
        all_samples = sorted(self.df["sample"].unique())
        temperatures = sorted(self.df["temperature"].unique())

        # Get selected samples
        selected_samples = [all_samples[i] for i in sample_indices]

        # Analyze patterns in sample names
        omas_patterns = set()
        temp_patterns = set()
        for sample in selected_samples:
            parts = sample.split("_")
            # Get OMAS_1-x pattern (first two parts)
            omas_pattern = "_".join(parts[:2])  # OMAS_1-x
            # Get temperature pattern (Txx) ignoring any suffixes
            temp_part = next((p for p in parts if p.startswith("T")), "")
            temp_pattern = temp_part.split("_")[0]  # Take only Txx part
            omas_patterns.add(omas_pattern)
            temp_patterns.add(temp_pattern)

        # Format sample names based on pattern changes
        formatted_samples = []
        xlabel = "Sample"  # Default xlabel
        for sample in selected_samples:
            parts = sample.split("_")
            if len(omas_patterns) == 1 and len(temp_patterns) > 1:
                # Only temperature changes, show Txx
                temp_part = next((p for p in parts if p.startswith("T")), "")
                formatted_samples.append(temp_part.split("_")[0])
                # Get the metal concentration (1/x) from the sample name
                ratio = parts[1].split("1-")[1]
                xlabel = f"OMAS 1/{ratio}"
            elif len(omas_patterns) > 1 and len(temp_patterns) == 1:
                # Only OMAS_1-x changes, show 1/x
                ratio = parts[1].split("1-")[1]
                formatted_samples.append(f"1/{ratio}")
                xlabel = "OMAS 1/x"
            else:
                # Both change or neither changes, show full name
                formatted_samples.append(sample)
                xlabel = "Sample"

        # Create figure with white background for display
        fig = plt.figure(figsize=(10, 6), facecolor="white")
        ax = fig.add_subplot(facecolor="white")

        # Remove grid
        ax.grid(False)

        # Set up bar width and positions
        bar_width = 0.8 / len(temperatures)
        x = np.arange(len(selected_samples))

        # Define colors for different temperatures
        if colors is None:
            colors = plt.cm.viridis(np.linspace(0, 1, len(temperatures)))

        # Plot bars for each temperature
        for i, temp in enumerate(temperatures):
            # Get data for this temperature and selected samples
            temp_data = self.df[
                (self.df["temperature"] == temp)
                & (self.df["sample"].isin(selected_samples))
            ]

            # Sort data to match selected_samples order
            temp_data = (
                temp_data.set_index("sample").reindex(selected_samples).reset_index()
            )

            # Get values for the selected acid type and option
            if acid_type == "lewis":
                values = (
                    temp_data["lewis_mmol_g"]
                    if option == "concentration"
                    else temp_data["lewis_nm2"]
                )
            else:
                values = (
                    temp_data["bronsted_mmol_g"]
                    if option == "concentration"
                    else temp_data["bronsted_nm2"]
                )

            # Plot bars
            ax.bar(
                x + i * bar_width,
                values,
                width=bar_width,
                color=colors[i],
                label=f"{temp}°C",
            )

        # Set labels
        ax.set_xlabel(xlabel)
        if acid_type == "lewis":
            if option == "concentration":
                ax.set_ylabel("$n_{LAS}$ / μmol g$^{-1}$")
            elif option == "surface_density":
                ax.set_ylabel("$n_{LAS}$ / nm$^{-2}$")
            else:  # surface_concentration
                ax.set_ylabel("$n_{LAS}$ / μmol nm$^{-2}$")
        else:
            if option == "concentration":
                ax.set_ylabel("$n_{BAS}$ / μmol g$^{-1}$")
            elif option == "surface_density":
                ax.set_ylabel("$n_{BAS}$ / nm$^{-2}$")
            else:  # surface_concentration
                ax.set_ylabel("$n_{BAS}$ / μmol nm$^{-2}$")

        # Format x-axis
        ax.set_xticks(x + bar_width * (len(temperatures) - 1) / 2)
        ax.set_xticklabels(formatted_samples, rotation=45, ha="right")

        # Set axis colors and ticks
        for spine in ax.spines.values():
            spine.set_color("black")
            spine.set_linewidth(1)

        ax.tick_params(
            axis="both",
            which="both",
            direction="out",
            length=6,
            width=1,
            colors="black",
            bottom=True,
            top=False,
            left=True,
            right=False,
        )

        # Add legend
        ax.legend(title="Temperature", frameon=False)

        # Adjust layout
        plt.tight_layout()

        # Save plot with transparent background
        if save_path:
            plt.savefig(save_path, dpi=600, transparent=True, bbox_inches="tight")
        else:
            # Create save path with xlabel
            save_path = f"acid_sites_bar_{acid_type}_{option}_{xlabel.replace(' ', '_').replace('/', '_')}.png"
            plt.savefig(save_path, dpi=600, transparent=True, bbox_inches="tight")

        # Show plot if requested
        if show:
            plt.show()
        else:
            plt.close()

        # Turn interactive mode back on
        plt.ion()

        return fig

    def plot_overview(
        self,
        sample_indices,
        option="concentration",
        save_path=None,
        show=True,
        colors=None,
    ):
        """Plot Lewis and Bronsted acid sites for multiple samples over desorption temperature.

        Args:
            sample_indices (list): List of sample indices to plot
            option (str, optional): Calculation option to plot, either "concentration", "surface_density", or "surface_concentration".
                                  Defaults to "concentration".
            save_path (str, optional): Path to save the plot. If None, saves as "acid_sites_overview_{option}.png"
            show (bool, optional): Whether to display the plot. Defaults to True.
            colors (list, optional): List of colors to use for the samples. If None, uses default colors.
        """
        # Get all available samples
        all_samples = sorted(self.df["sample"].unique())
        selected_samples = [all_samples[i] for i in sample_indices]

        # Create figure with two y-axes
        fig = plt.figure(figsize=(8, 6), facecolor="white")
        ax1 = fig.add_subplot(facecolor="white")
        ax2 = ax1.twinx()

        # Remove grid
        ax1.grid(False)
        ax2.grid(False)

        # Define colors and markers
        if colors is None:
            colors = ["black" "red", "blue", "green", "orange"]
        markers = ["o", "v", "s", "h", "*"]

        # Plot data for each sample
        for i, sample in enumerate(selected_samples):
            sample_data = self.df[self.df["sample"] == sample]

            # Plot Lewis acid sites
            ax1.plot(
                sample_data["temperature"],
                (
                    sample_data["lewis_mmol_g"]
                    if option == "concentration"
                    else sample_data["lewis_nm2"]
                ),
                color=colors[i % len(colors)],
                marker=markers[i % len(markers)],
                linestyle="None",
                label=sample,
                fillstyle="full",
            )

            # Plot Bronsted acid sites
            ax2.plot(
                sample_data["temperature"],
                (
                    sample_data["bronsted_mmol_g"]
                    if option == "concentration"
                    else sample_data["bronsted_nm2"]
                ),
                color=colors[i % len(colors)],
                marker=markers[i % len(markers)],
                linestyle="None",
                label=None,
                fillstyle="none",
                markeredgewidth=1.5,
            )

        # Set labels and limits
        ax1.set_xlabel("$T_{Des}$ / °C")
        if option == "concentration":
            ax1.set_ylabel("$n_{LAS}$ / μmol g$^{-1}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / μmol g$^{-1}$" + " ○", color="dimgrey")
        elif option == "surface_density":
            ax1.set_ylabel("$n_{LAS}$ / nm$^{-2}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / nm$^{-2}$" + " ○", color="dimgrey")
        else:  # surface_concentration
            ax1.set_ylabel("$n_{LAS}$ / μmol nm$^{-2}$" + " ●", color="black")
            ax2.set_ylabel("$n_{BAS}$ / μmol nm$^{-2}$" + " ○", color="dimgrey")

        # Set axis colors, linewidths, and ticks
        for spine in ax1.spines.values():
            spine.set_color("black")
            spine.set_linewidth(1)
        for spine in ax2.spines.values():
            spine.set_color("dimgrey")
            spine.set_linewidth(1)

        # Configure ticks for both axes
        ax1.tick_params(
            axis="both",
            which="both",
            direction="out",
            length=6,
            width=1,
            colors="black",
            bottom=True,
            top=False,
            left=True,
            right=False,
        )

        ax2.tick_params(
            axis="y",
            which="both",
            direction="out",
            length=6,
            width=1,
            colors="dimgrey",
            left=False,
            right=True,
        )

        # Add legend
        ax1.legend(frameon=False)

        # Adjust layout
        plt.tight_layout()

        # Save plot
        if save_path:
            plt.savefig(save_path, dpi=600, transparent=True, bbox_inches="tight")
        else:
            plt.savefig(
                f"acid_sites_overview_{option}.png",
                dpi=600,
                transparent=True,
                bbox_inches="tight",
            )

        # Show plot if requested
        if show:
            plt.show()
        else:
            plt.close()

        return fig

    def plot_single_axis(
        self,
        sample_indices,
        acid_type="lewis",
        option="concentration",
        save_path=None,
        show=True,
        colors=None,
    ):
        """Plot acid sites for multiple samples over desorption temperature using a single y-axis.

        Args:
            sample_indices (list): List of sample indices to plot
            acid_type (str, optional): Type of acid site to plot, either "lewis" or "bronsted". Defaults to "lewis".
            option (str, optional): Calculation option to plot, either "concentration", "surface_density", or "surface_concentration".
                                  Defaults to "concentration".
            save_path (str, optional): Path to save the plot. If None, saves as "acid_sites_single_{acid_type}_{option}.png"
            show (bool, optional): Whether to display the plot. Defaults to True.
            colors (list, optional): List of colors to use for the samples. If None, uses default colors.
        """
        # Get all available samples
        all_samples = sorted(self.df["sample"].unique())
        selected_samples = [all_samples[i] for i in sample_indices]

        # Create figure
        fig = plt.figure(figsize=(8, 6), facecolor="white")
        ax = fig.add_subplot(facecolor="white")

        # Remove grid
        ax.grid(False)

        # Define colors and markers
        if colors is None:
            colors = ["black", "red", "blue", "green", "orange"]
        markers = ["o", "v", "s", "h", "*"]

        # Plot data for each sample
        for i, sample in enumerate(selected_samples):
            sample_data = self.df[self.df["sample"] == sample]

            # Plot acid sites
            values = (
                (
                    sample_data["lewis_mmol_g"]
                    if acid_type == "lewis"
                    else sample_data["bronsted_mmol_g"]
                )
                if option == "concentration"
                else (
                    sample_data["lewis_nm2"]
                    if acid_type == "lewis"
                    else sample_data["bronsted_nm2"]
                )
            )

            ax.plot(
                sample_data["temperature"],
                values,
                color=colors[i % len(colors)],
                marker=markers[i % len(markers)],
                linestyle="None",
                label=sample,
                fillstyle="full" if acid_type == "lewis" else "none",
                markeredgewidth=1.5 if acid_type == "bronsted" else 1,
            )

        # Set labels and limits
        ax.set_xlabel("$T_{Des}$ / °C")
        if acid_type == "lewis":
            if option == "concentration":
                ax.set_ylabel("$n_{LAS}$ / μmol g$^{-1}$")
            elif option == "surface_density":
                ax.set_ylabel("$n_{LAS}$ / nm$^{-2}$")
            else:  # surface_concentration
                ax.set_ylabel("$n_{LAS}$ / μmol nm$^{-2}$")
        else:
            if option == "concentration":
                ax.set_ylabel("$n_{BAS}$ / μmol g$^{-1}$")
            elif option == "surface_density":
                ax.set_ylabel("$n_{BAS}$ / nm$^{-2}$")
            else:  # surface_concentration
                ax.set_ylabel("$n_{BAS}$ / μmol nm$^{-2}$")

        # Set axis colors and ticks
        for spine in ax.spines.values():
            spine.set_color("black")
            spine.set_linewidth(1)

        ax.tick_params(
            axis="both",
            which="both",
            direction="out",
            length=6,
            width=1,
            colors="black",
            bottom=True,
            top=False,
            left=True,
            right=False,
        )

        # Add legend
        ax.legend(frameon=False)

        # Adjust layout
        plt.tight_layout()

        # Save plot
        if save_path:
            plt.savefig(save_path, dpi=600, transparent=True, bbox_inches="tight")
        else:
            plt.savefig(
                f"acid_sites_single_{acid_type}_{option}.png",
                dpi=600,
                transparent=True,
                bbox_inches="tight",
            )

        # Show plot if requested
        if show:
            plt.show()
        else:
            plt.close()

        return fig
