import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load data
df_Day = pd.read_csv("data\day.csv")
df_Hour = pd.read_csv("data\hour.csv")

# Preprocessing
df_Day = df_Day.drop(columns=["instant", "yr", "mnth"])
season_labels = {1: "winter", 2: "spring", 3: "summer", 4: "fall"}
df_Day["season"] = df_Day["season"].replace(season_labels)
weekday_map = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
}
df_Day["weekday"] = df_Day["weekday"].map(weekday_map)

df_Hour = df_Hour.drop(columns=["instant", "yr", "mnth"])
season_labels = {1: "winter", 2: "spring", 3: "summer", 4: "fall"}
df_Hour["season"] = df_Hour["season"].replace(season_labels)
weekday_map = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
}
df_Hour["weekday"] = df_Hour["weekday"].map(weekday_map)

# Monthly Rentals
df_Day["dteday"] = pd.to_datetime(df_Day["dteday"])
df_Day["year_month"] = df_Day["dteday"].dt.to_period("M")
monthly_rentals = (
    df_Day.groupby("year_month")[["casual", "registered", "cnt"]].sum().reset_index()
)
monthly_rentals["year_month"] = monthly_rentals["year_month"].dt.to_timestamp()

# Seasonal Rentals
season_order = ["spring", "summer", "fall", "winter"]
df_Day["season"] = pd.Categorical(
    df_Day["season"], categories=season_order, ordered=True
)
seasonal_rentals = df_Day.groupby("season")[["cnt"]].sum().reset_index()

# Weather Rentals
weather_data = df_Day.groupby("weathersit")["cnt"].sum().reset_index()

# Weekly Rentals
weekly_rentals = df_Day.groupby("weekday")["cnt"].sum().reset_index()

# Day Type Rentals
day_type_df = df_Day.copy()

day_type_df["day_type"] = day_type_df.apply(
    lambda row: (
        "Holiday & Non-Working Day"
        if row["holiday"] == 1 and row["workingday"] == 0
        else (
            "Holiday & Working Day"
            if row["holiday"] == 1 and row["workingday"] == 1
            else (
                "Non-Holiday & Working Day"
                if row["holiday"] == 0 and row["workingday"] == 1
                else "Non-Holiday & Non-Working Day"
            )
        )
    ),
    axis=1,
)

day_type_data = day_type_df.groupby("day_type")["cnt"].sum().reset_index()
day_type_data.rename(columns={"cnt": "Total Rentals"}, inplace=True)

# Hourly Rentals
working_day_data = df_Hour[df_Hour["workingday"] == 1]
hourly_rentals_working_day = working_day_data.groupby("hr")["cnt"].sum().reset_index()

non_working_day_data = df_Hour[df_Hour["workingday"] == 0]
hourly_rentals_non_working_day = (
    non_working_day_data.groupby("hr")["cnt"].sum().reset_index()
)

# Hourly Rentals by Season
winter_data = df_Hour[df_Hour["season"] == "winter"]
spring_data = df_Hour[df_Hour["season"] == "spring"]
summer_data = df_Hour[df_Hour["season"] == "summer"]
fall_data = df_Hour[df_Hour["season"] == "fall"]

hourly_rentals_winter = winter_data.groupby("hr")["cnt"].sum().reset_index()
hourly_rentals_spring = spring_data.groupby("hr")["cnt"].sum().reset_index()
hourly_rentals_summer = summer_data.groupby("hr")["cnt"].sum().reset_index()
hourly_rentals_fall = fall_data.groupby("hr")["cnt"].sum().reset_index()

# Sidebar menu
menu = st.sidebar.radio(
    "Menu",
    [
        "Dataset Overview",
        "Monthly Rentals",
        "Seasonal Rentals",
        "Weather Rentals",
        "Weekly Rentals",
        "Day Type Rentals",
        "Weather Influence",
        "Hourly Rentals",
        "Hourly Rentals by Season",
    ],
)

# Dataset Overview
if menu == "Dataset Overview":
    st.title("Bike Sharing Dataset Overview")

    # Dataset description
    st.write(
        """
        ### Dataset Information 
        Bike sharing systems are a new generation of traditional bike rentals where the entire process of membership, rental, and return has become automatic. Through these systems, users can easily rent a bike from one station and return it to another. Currently, there are over 500 bike-sharing programs worldwide, consisting of more than 500,000 bicycles. These systems are gaining attention due to their significant role in traffic management, environmental preservation, and health improvement.

        The characteristics of the data generated by these systems make them particularly attractive for research. Unlike other forms of public transport such as buses or subways, bike sharing systems record explicit data on the duration of trips, departure, and arrival locations. This data can serve as a 'virtual sensor network' for monitoring city mobility patterns. Therefore, monitoring bike-sharing data has the potential to detect significant events and trends in the city.
        """
    )

    # Display the head of df_Day DataFrame
    st.write("### df_Day DataFrame (First 5 Rows)")
    st.write(df_Day.head())

    # Display the head of df_Hour DataFrame
    st.write("### df_Hour DataFrame (First 5 Rows)")
    st.write(df_Hour.head())

    # Detailed explanation of each column
    st.write(
        """
        ### Dataset Columns Description
        - **instant**: Record index
        - **dteday**: Date
        - **season**: Season (1: winter, 2: spring, 3: summer, 4: fall)
        - **yr**: Year (0: 2011, 1: 2012)
        - **mnth**: Month (1 to 12)
        - **hr**: Hour of the day (0 to 23)
        - **holiday**: Whether the day is a holiday (1: holiday, 0: not a holiday)
        - **weekday**: Day of the week (0: Sunday, 1: Monday, ..., 6: Saturday)
        - **workingday**: Whether the day is a working day (1: working day, 0: weekend/holiday)
        - **weathersit**: Weather condition:
          - 1: Clear, Few clouds, Partly cloudy
          - 2: Mist + Cloudy, Mist + Broken clouds
          - 3: Light Snow, Light Rain + Thunderstorm
          - 4: Heavy Rain + Ice Pallets, Snow + Fog
        - **temp**: Normalized temperature in Celsius (scaled between -8°C and 39°C)
        - **atemp**: Normalized apparent (feels-like) temperature (scaled between -16°C and 50°C)
        - **hum**: Normalized humidity (divided by 100)
        - **windspeed**: Normalized wind speed (divided by 67)
        - **casual**: Count of casual users (non-registered)
        - **registered**: Count of registered users
        - **cnt**: Total count of rentals (casual + registered)
        """
    )

# Monthly Rentals
elif menu == "Monthly Rentals":
    st.title("Monthly Rentals")

    # Display the monthly rentals DataFrame
    st.write("### Monthly Rentals Data")
    st.write(monthly_rentals)

    # Plot the monthly rentals
    plt.figure(figsize=(12, 6))
    plt.plot(
        monthly_rentals["year_month"],
        monthly_rentals["casual"],
        marker="o",
        label="Casual Rentals",
        color="blue",
    )
    plt.plot(
        monthly_rentals["year_month"],
        monthly_rentals["registered"],
        marker="o",
        label="Registered Rentals",
        color="orange",
    )
    plt.plot(
        monthly_rentals["year_month"],
        monthly_rentals["cnt"],
        marker="o",
        label="Total Rentals",
        color="green",
    )

    plt.title("Total Monthly Bike Rentals")
    plt.xlabel("Month")
    plt.ylabel("Total Rentals")
    plt.xticks(
        monthly_rentals["year_month"],
        monthly_rentals["year_month"].dt.strftime("%b %Y"),
        rotation=45,
    )
    plt.legend()
    plt.grid()

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Explanation of rental patterns
    st.write(
        """
        ### Insight:
        - Pola total rental untuk setiap tahunnya cenderung sama, yaitu naik saat awal tahun dan turun saat akhir tahun.
        - Pada tahun 2011 kenaikan total rental yang signifikan terjadi di bulan Maret hingga Mei, lalu setelah itu mulai turun perlahan menuju akhir tahun.
        - Pada tahun 2012 kenaikan total rental yang signifikan terjadi di bulan Februari hingga Mei, lalu stabil di bulan Mei hingga September, kemudian turun secara drastis menuju akhir tahun.
        - Total rental terbanyak terjadi di bulan September tahun 2012.
        - Pola total rental, casual rental, dan registered rental cenderung sama.
        """
    )

# Seasonal Rentals
elif menu == "Seasonal Rentals":
    st.title("Seasonal Rentals")

    # Display the seasonal rentals DataFrame
    st.write("### Seasonal Rentals Data")
    st.write(seasonal_rentals)

    # Plot the seasonal rentals
    plt.figure(figsize=(10, 6))
    seasonal_rentals.set_index("season").plot(kind="bar", color="orange", ax=plt.gca())

    plt.title("Total Bike Rentals per Season")
    plt.xlabel("Season")
    plt.ylabel("Total Rentals")
    plt.xticks(rotation=0)
    plt.grid(axis="y")

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Explanation of seasonal rental patterns
    st.write(
        """
        ### Insight:
        - Musim mempengaruhi total rental.
        - Total rental terbanyak terjadi di musim panas (summer).
        - Total rental tersedikit terjadi di musim dingin (winter).
        """
    )

# Weather Rentals
elif menu == "Weather Rentals":
    st.title("Weather Rentals")

    # Display the weather data DataFrame
    st.write("### Weather Rentals Data")
    st.write(weather_data)

    # Plot the weather data
    plt.figure(figsize=(10, 6))
    weather_data.plot(kind="bar", color="skyblue", ax=plt.gca())

    plt.title("Total Rentals by Weather Situation")
    plt.xlabel("Weather Situation")
    plt.ylabel("Total Rentals")
    plt.xticks(
        ticks=[0, 1, 2, 3],
        labels=[
            "Clear/Partly Cloudy",
            "Mist/Cloudy",
            "Light Rain/Snow",
            "Heavy Rain/Fog",
        ],
        rotation=0,
    )
    plt.grid(axis="y")

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Explanation of weather rental patterns
    st.write(
        """
        ### Insight:
        - Cuaca mempengaruhi total rental.
        - Sebagian besar orang memilih rental sepeda pada cuaca cerah (clear/partly cloudy) dan berawan (mist/cloudy).
        - Ada sedikit orang yang merental sepeda pada cuaca hujan ringan (light rain/snow).
        - Tidak ada orang yang merental sepeda pada cuaca hujan lebat (heavy rain/fog).
        """
    )

# Weekly Rentals
elif menu == "Weekly Rentals":
    st.title("Weekly Rentals")

    # Display the weekly rentals DataFrame
    st.write("### Weekly Rentals Data")
    st.write(weekly_rentals)

    # Plot the weekly rentals as a pie chart
    plt.figure(figsize=(8, 8))
    labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    plt.pie(weekly_rentals["cnt"], labels=labels, autopct="%1.1f%%", startangle=90)

    plt.title("Total Rentals by Day of the Week")
    plt.axis("equal")

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Explanation of weekly rental patterns
    st.write(
        """
        ### Insight:
        - Hari tidak terlalu mempengaruhi jumlah rental.
        """
    )

# Day Type Rentals
elif menu == "Day Type Rentals":
    st.title("Day Type Rentals")

    # Display the day type data DataFrame
    st.write("### Day Type Rentals Data")
    st.write(day_type_data)

    # Plot the day type rentals as a pie chart
    plt.figure(figsize=(8, 8))
    day_type_data.set_index("day_type").plot.pie(
        y="Total Rentals",
        autopct="%1.1f%%",
        colors=["lightblue", "lightgreen", "lightcoral", "lightyellow"],
        title="Total Rentals by Day Type",
        legend=False,
        ax=plt.gca(),
    )
    plt.ylabel("")
    plt.axis("equal")

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Explanation of day type rental patterns
    st.write(
        """
        - Sebagian besar orang (69.6%) merental sepeda di hari kerja.
        - 28% orang merental sepeda saat bukan hari kerja, tetapi bukan hari libur.
        - 2.4% orang merental sepeda saat hari libur.
        """
    )

# Weather Influence on Rentals
elif menu == "Weather Influence":
    st.title("Weather Influence on Rentals")

    # Display the scatter plots
    st.write("### Scatter Plots of Total Rentals by Weather Variables")

    # Scatter plot for normalized temperature
    plt.figure(figsize=(10, 6))
    plt.scatter(df_Day["temp"], df_Day["cnt"], color="blue", alpha=0.5)
    plt.title("Scatter Plot of Total Rentals by Temperature")
    plt.xlabel("Normalized Temperature")
    plt.ylabel("Total Rentals")
    plt.grid(True)
    st.pyplot(plt)

    # Correlation between temperature and total rentals
    correlation_temp = df_Day[["temp", "cnt"]].corr().iloc[0, 1]
    st.write(
        f"**Correlation between Normalized Temperature and Total Rentals: {correlation_temp:.4f}**"
    )

    # Scatter plot for normalized apparent temperature
    plt.figure(figsize=(10, 6))
    plt.scatter(df_Day["atemp"], df_Day["cnt"], color="orange", alpha=0.5)
    plt.title("Scatter Plot of Total Rentals by Apparent Temperature")
    plt.xlabel("Normalized Apparent Temperature")
    plt.ylabel("Total Rentals")
    plt.grid(True)
    st.pyplot(plt)

    # Correlation between apparent temperature and total rentals
    correlation_atemp = df_Day[["atemp", "cnt"]].corr().iloc[0, 1]
    st.write(
        f"**Correlation between Normalized Apparent Temperature and Total Rentals: {correlation_atemp:.4f}**"
    )

    # Scatter plot for normalized humidity
    plt.figure(figsize=(10, 6))
    plt.scatter(df_Day["hum"], df_Day["cnt"], color="green", alpha=0.5)
    plt.title("Scatter Plot of Total Rentals by Humidity")
    plt.xlabel("Normalized Humidity")
    plt.ylabel("Total Rentals")
    plt.grid(True)
    st.pyplot(plt)

    # Correlation between humidity and total rentals
    correlation_hum = df_Day[["hum", "cnt"]].corr().iloc[0, 1]
    st.write(
        f"**Correlation between Normalized Humidity and Total Rentals: {correlation_hum:.4f}**"
    )

    # Scatter plot for normalized wind speed
    plt.figure(figsize=(10, 6))
    plt.scatter(df_Day["windspeed"], df_Day["cnt"], color="red", alpha=0.5)
    plt.title("Scatter Plot of Total Rentals by Wind Speed")
    plt.xlabel("Normalized Wind Speed")
    plt.ylabel("Total Rentals")
    plt.grid(True)
    st.pyplot(plt)

    # Correlation between wind speed and total rentals
    correlation_windspeed = df_Day[["windspeed", "cnt"]].corr().iloc[0, 1]
    st.write(
        f"**Correlation between Normalized Wind Speed and Total Rentals: {correlation_windspeed:.4f}**"
    )

    # Explanation of weather influence on rentals
    st.write(
        """
        ### Insight:
        - Terdapat korelasi positif yang kecil antara total rental dengan temperature.
        - Terdapat korelasi positif yang kecil antara total rental dengan apparent temperature
        - Total rental tidak dipengaruhi oleh kelembapan (humidity).
        - Total rental tidak dipengaruhi oleh kecepatan angin (wind speed).
        """
    )


# Hourly Rentals
elif menu == "Hourly Rentals":
    st.title("Hourly Rentals")

    # Display the hourly rentals for working days
    st.write("### Total Rentals by Hour of the Day (Working Days)")

    # Plot for working days
    plt.figure(figsize=(10, 6))
    plt.plot(
        hourly_rentals_working_day["hr"],
        hourly_rentals_working_day["cnt"],
        marker="o",
        color="purple",
    )
    plt.title("Total Rentals by Hour of the Day (Working Days)")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Total Rentals (Working Days)")
    plt.xticks(hourly_rentals_working_day["hr"])
    plt.grid(True)

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Explanation of hourly rental patterns
    st.write(
        """
        ### Insight:
        - Pada hari kerja, orang cenderung merental sepeda pada pagi hari dan sore hari.
        - Pada pagi hari, orang mulai merental dari jam 5:00 hingga puncaknya di jam 8:00.
        - Pada sore hari, orang mulai merental dari jam 15:00 hingga puncaknya di jam 17:00.
        """
    )

    # Display the hourly rentals for non-working days
    st.write("### Total Rentals by Hour of the Day (Non-Working Days)")

    # Plot for non-working days
    plt.figure(figsize=(10, 6))
    plt.plot(
        hourly_rentals_non_working_day["hr"],
        hourly_rentals_non_working_day["cnt"],
        marker="o",
        color="red",
    )
    plt.title("Total Rentals by Hour of the Day (Non-Working Days)")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Total Rentals (Non-Working Days)")
    plt.xticks(hourly_rentals_non_working_day["hr"])
    plt.grid(True)

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Explanation of hourly rental patterns
    st.write(
        """
        ### Insight:
        - Di hari bukan hari kerja, orang mulai merental dari pagi jam 6:00 hingga puncaknya di jam 12:00 sampai 16:00, lalu turun setelah itu.
        """
    )

# Hourly Rentals by Season
elif menu == "Hourly Rentals by Season":
    st.title("Hourly Rentals by Season")

    # Display the hourly rentals data
    st.write("### Total Rentals by Hour of the Day (All Seasons)")

    # Plot hourly rentals for all seasons
    plt.figure(figsize=(10, 6))
    plt.plot(
        hourly_rentals_winter["hr"],
        hourly_rentals_winter["cnt"],
        marker="o",
        color="blue",
        label="Winter",
    )
    plt.plot(
        hourly_rentals_spring["hr"],
        hourly_rentals_spring["cnt"],
        marker="o",
        color="green",
        label="Spring",
    )
    plt.plot(
        hourly_rentals_summer["hr"],
        hourly_rentals_summer["cnt"],
        marker="o",
        color="orange",
        label="Summer",
    )
    plt.plot(
        hourly_rentals_fall["hr"],
        hourly_rentals_fall["cnt"],
        marker="o",
        color="red",
        label="Fall",
    )

    # Set titles and labels
    plt.title("Total Rentals by Hour of the Day (All Seasons)")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Total Rentals")
    plt.xticks(hourly_rentals_winter["hr"])
    plt.grid(True)
    plt.legend()

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Explanation of seasonal rental patterns by hour
    st.write(
        """
        ### Insight:
        - Pola total rental tiap jam untuk semua musim cenderung sama.
        - Sama seperti visualisasi total rental setiap musim, untuk total rental paling banyak terjadi di musim panas (summer) dan paling sedikit terjadi di musim dingin (winter).        """
    )
