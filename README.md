# AE_sizing_tool

## Description

This project is a sizing tool developed for the AE6343 course at Georgia Institute of Technology. It aims to assist in the preliminary design and sizing of aerospace vehicles. The tool might not be accurate and could contain errors. A detailed report is available to explain the process of the tool design.

## Installation

To install the tool, follow these steps. Two options are available to install the tool.

### Option 1: Using git

1. Clone the repository:
    ```bash
    git clone https://github.com/aeomath/AE_sizing_tool.git
    ```
2. Navigate to the project directory:
    ```bash
    cd AE_sizing_tool
    ```

### Option 2: Downloading the zip file

1. Unzip the downloaded file and navigate to the project directory:
    ```bash
    cd AE_sizing_tool
    ```
2. Create a virtual environment using conda or venv (using Python 3.10 if possible):
   Using venv
    ```bash
    python -m venv venv
    ```
    or using conda
    ```bash
    conda create --name venv python=3.10
    ```
4. Install the required dependencies **in your environment** :
    ```bash
    (env)$ pip install -r requirements.txt
    ```

## Usage

To use the tool, you need inputs. Inputs are located in the `Inputs` folder in JSON files.

### Use the existing example

A set of example input files are provided in the `Inputs` folder. These files contain the necessary parameters for the sizing calculations for the mission given in the project for an A320. You can use these files to test the tool and see how it works.

To run the tool with the provided example inputs, simply run the main script:
```bash
python Main.py
```
> Run time can take up to 2 minutes depending on the computer's performance. Please be patient. A prohgress bar will be displayed in the console to show the progress of the calculations. usually, the numbers of iterations are 3.

### Input your own parameters

If you want to use your own parameters, you can create your own input files. You need to provide input files in JSON format. These input files should be placed in the `Inputs` folder. Each JSON file should contain the necessary parameters for the sizing calculations.

Here is an example of what an input JSON file might look like:

```json
{
    "parameter1": "value1",
    "parameter2": "value2",
    "parameter3": "value3"
}
```

Make sure to adjust the parameters and values according to your specific requirements.

Five input files are provided in the `Inputs` folder. You can use them as a reference to create your own input files:

* `aerodynamics.json`: This file contains the aerodynamics constants K1, K2.
* `propulsion.json`: This file contains the propulsion constants.
* `structural.json`: This file contains the structural constants such as kWE.

These three files cannot be renamed or modified; the program will not run correctly if you do so.

* `Mission_Profile.json`: This file contains the mission profile segments. Feel free to modify any phases or add new ones using this example.

> **Careful**: You need specific parameters for each phase. Check the provided `Mission_Profile.json` file to see which parameters are required for each phase so the program can run correctly.

Here is a list of the available phases you can add:

* Taxi
* Takeoff
* Climb
* Acceleration
* Cruise
* Loiter (in the `cruise.py` file)
* Deceleration (acceleration with start speed inferior to end speed)
* Cruise
* Descent (climb with negative rate or flight path angle)
* Approach
* Landing

To run the tool with your own input files, be careful to modify the name of the inputs file in the `Main.py` and simply run the main script:
```bash
python Main.py < My_Mission_Profile.json >
```
## Output

After Running the tool , mains results will be printed in a console graphs will be generated 
* The first graph shows the constraints analysis plot.
* The second graph shows the Weight_Breakdown and the weight decomposition.
* The third graph shows some aerodynamics and propulsion characteristics. A dropdown menu is available to select the parameter to display.
> The graphs are interactive, and you can zoom in and out, pan, and save them as images.
> All data you see on this graph are datas at the end of the segment.
>**If the graphs are not displayed, please refresh the page (F5) where the graphs are displayed. (sometimes Plotly has issues with displaying the graphs)**

### Output folder ### 
All the results will be saved in the `outputs` folder in  HTML files you can open it in your browser.
## Contributing

Contributions are welcome! Please fork the repository and create a pull request.
