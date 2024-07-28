# Practice Calclulators

This project is a Streamlit-based dashboard designed to help visualize and optimize practice variables for both surgeons and non-surgeon providers. It allows users to adjust various parameters to see how they affect metrics such as wRVUs, patient counts, and revenue projections.

## Features

- **General Settings**: Configure the number of new and established patients per session, sessions per week, and weeks per year.
- **Diagnosis Group Distribution**: Adjust the percentage distribution of different diagnosis groups.
- **Juice to Squeeze Ratio**: Define the percentage of patients who will undergo surgical or advanced therapy within six months.
- **New and Established Patient Charge Distribution**: Set the distribution of billing codes for new and established patients.
- **Average wRVU per Case**: Input the average wRVUs for different types of cases.
- **Projections and Summaries**: View detailed wRVU summaries, patient counts, and code counts in a tabular format.

## Installation

To run this dashboard locally, you need to have Python installed. Follow these steps to set up the project:

1. Clone the repository:
    ```bash
    git clone https://github.com/stuboo/practice_calculator.git
    cd practice_calculator
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

## Usage

Once the app is running, you can access it in your web browser. The dashboard has two main tabs:

### Main Projections

- Adjust settings for new patients, sessions per week, and weeks per year.
- Configure diagnosis group distributions and juice to squeeze ratios.
- Set distributions for new patient charge codes.
- Input average wRVUs for different types of cases.
- View projections and summaries for wRVUs.

### Additional Calculations

- Similar settings as the Main Projections tab but geared towards non-surgeon providers.
- Includes settings for both new and established patients.
- View detailed wRVU summaries, patient counts, and code counts.

## Customization

You can customize the dashboard by modifying the code in `app.py`. The `ProjectionCalculator` class encapsulates the logic for calculating projections and can be extended or modified to fit different requirements.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please open an issue in the repository or contact the project maintainer.