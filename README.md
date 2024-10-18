# AE_sizing_tool
[![Author Badge](https://img.shields.io/badge/Author-Adam%20Benabou-blue?style=for-the-badge&logo=github&logoColor=white&labelColor=blue&color=blue&link=https://github.com/aeomath)](https://github.com/aeomath) ![Date Badge](https://img.shields.io/badge/Date-October%202023-orange?style=for-the-badge&logo=github&logoColor=white&labelColor=orange&color=orange&link=https://github.com/aeomath) 

[![Institution Badge](https://img.shields.io/badge/Institution-Georgia%20Institute%20of%20Technology-yellow?style=for-the-badge&logo=github&logoColor=white&labelColor=yellow&color=yellow&link=https://ae.gatech.edu/)](https://ae.gatech.edu/)

![Python Badge](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white&labelColor=blue&color=blue)


This project is a sizing tool developed for the AE6343 course at Georgia Institute of Technology. It aims to assist in the preliminary design and sizing of aerospace vehicles. The tool might not be accurate and could contain errors. A detailed report is available to explain the process of the tool design.


## Table of Contents ##

1. [Installation](#installation)
    - [Option 1: Using git](#option-1-using-git)
    - [Option 2: Downloading the zip file](#option-2-downloading-the-zip-file)
2. [Usage](#usage)
    - [Use the existing example](#use-the-existing-example)
    - [Input your own parameters](#input-your-own-parameters)
3. [Output](#output)
    - [Output folder](#output-folder)
    
4. [Contributing](#contributing)


## Installation ##

To install the tool, follow these steps. Two options are available to install the tool.

### Option 1: Using  git ###

1. Clone the repository:
    ```bash
    git clone https://github.com/aeomath/AE_sizing_tool.git
    ```
2. Navigate to the project directory:
    ```bash
    cd AE_sizing_tool
    ```
3. Create a virtual environment using conda or venv (using Python 3.10 if possible):
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

### Option 2: Downloading the zip file ###

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

## Usage ##

To use the tool, you need inputs. Inputs are located in the `Inputs` folder in JSON files.

### Use the existing example ###

A set of example input files are provided in the `Inputs` folder. These files contain the necessary parameters for the sizing calculations for the mission given in the project for an A320. You can use these files to test the tool and see how it works.

To run the tool with the provided example inputs, simply run the main script:
```bash
python Main.py
```
> Run time can take up to 2 minutes depending on the computer's performance. Please be patient. A prohgress bar will be displayed in the console to show the progress of the calculations. usually, the numbers of iterations are 3.

### Input your own  ###

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
## Output ##

After Running the tool , mains results will be printed in a console and graphs will be generated 
* The first graph shows the constraints analysis plot.
* The second graph shows the Weight_Breakdown and the weight decomposition.
* The third graph shows some aerodynamics and propulsion characteristics. A dropdown menu is available to select the parameter to display.
* The fourth graph shows the instantaneous T/W and W/S ratios for each segment.
> The graphs are interactive, and you can zoom in and out, pan, and save them as images.
> All data you see on this graph are datas at the end of the segment.
>**If the graphs are not displayed, please refresh the page (F5) where the graphs are displayed. (sometimes Plotly has issues with displaying the graphs)**

### Output folder ### 
All the results will be saved in the `outputs` folder in  HTML files you can open it in your browser.
1. ``aero_and_prop_characteristics.html``
   This graph plots several aerodynamics and propulsion characteristics.
   
2. ``combined_weight_plot.html``
   This graph shows the converged weight breakdown and plots the weight of the aircraft at each phase.
   
3. ``Constraint_analysis.html``
   This is the constraint analysis plot.
   
4. ``final_design_results.html`` 
   This file summarizes the value of the main variables computed by the tool (WSR, TWR, Wingspan, Wing Area, TOW ...).
   
5. ``TWR_and_WSR_per_phase.html``
   This graph shows the instantaneous T/W and W/S ratios for each segment.

## Contributing ##

Contributions are welcome! Please fork the repository and create a pull request.
