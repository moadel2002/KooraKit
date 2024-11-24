# Koora-Kit: Your Ultimate Football Analysis Tool

Welcome to **Koora-Kit**, the one-stop platform for comprehensive pre-match and post-match analysis of football matches and players. Whether you are a passionate fan, a tactical enthusiast, or a professional analyst, Koora-Kit is designed to provide you with actionable insights and detailed evaluations of every aspect of the beautiful game.

# What is Koora-Kit?
Koora-Kit empowers users to explore football data intuitively and insightfully. By combining advanced analytics, rich visualizations, and user-friendly interfaces, it enables a deep dive into: 
* Pre-Match Analysis: Evaluate team strategies, player form, and key statistics to predict match outcomes or prepare for game day.
* Post-Match Breakdown: Gain insights into team performance, player contributions, and pivotal moments with data-driven evaluations.

# Key Features:
* Pre-Match Analysis:
    * **Team Comparisons**: Analyze strengths, weaknesses, and trends for both competing teams.
    * **Player Comparisons**: Analyze strengths, weaknesses, and trends for different players.
    * **Player Performance** Metrics: Dive deep into player statistics to understand individual contributions.
    * **Customizable Reports**: Generate reports using LLMs to differentiate between two players in terms of their KPIs.
![Screenshot from 2024-11-24 16-10-21](https://github.com/user-attachments/assets/a2e9f6fb-f9f8-4468-ad81-370f94b3dfcb)

Below is a video showing the Pre-Match Analytics (Video Here)

* Post-Match Analysis:
    * **Player Detection and Tracking**: Automatically identify and track player movements throughout the match using YOLOv8 and Deep-EIOU tracker.
    * **Ball Detection and Tracking**: Monitor the ball's position and movement, capturing key moments and transitions during gameplay using YOLOv8.
      ![Screenshot from 2024-11-24 16-36-40](https://github.com/user-attachments/assets/f0ed65f5-7570-4457-ad61-410b119ccb6c)
      ![Screenshot from 2024-11-24 16-37-32](https://github.com/user-attachments/assets/8e0af2d1-c1b3-4676-a6c5-8ef0e58a08fd)
      ![Screenshot from 2024-11-24 16-37-42](https://github.com/user-attachments/assets/661ae6d3-29bd-4479-be55-6842d52b6eb8)
    * **Team Assignment**: Assign detected players to their respective teams using KMeans on players' VGG19 embeddings.
      ![Screenshot from 2024-11-24 16-39-12](https://github.com/user-attachments/assets/dc43fd9e-86eb-46ea-9499-2c8ee80435e8)
      ![Screenshot from 2024-11-24 16-40-28](https://github.com/user-attachments/assets/5c3a0769-8d91-493f-ac55-e60e7958b761)
    * **Field Localization**: Detecting the field's key points using YOLOv8pose to map all activities onto the football pitch for spatial and tactical insights, such as heatmaps and formation       analysis.
      ![Screenshot from 2024-11-24 16-42-55](https://github.com/user-attachments/assets/25c73cc8-158c-4998-b3ed-0825292893a9)
      ![Screenshot from 2024-11-24 16-42-06](https://github.com/user-attachments/assets/3ad9bdea-c530-4ab3-95cf-ed84d36f1385)

  Using the output of these models, the following analytics were driven:
    * **Heatmap calculation**: it highlights the areas where the player was most or least effective.
      (Video)
    * **Speed and Distance Calculation**: it calculates the average speed and distance of each player throughout the match.

The whole post-processing pipeline is shown below:
  ![Screenshot from 2024-11-24 16-50-07](https://github.com/user-attachments/assets/5c796f8a-47c5-42d9-8779-554e009c4abe)

All of the detection and field localization models were fine-tuned on [Soccernet](https://www.soccer-net.org/tasks) dataset

The models' weights can be found in this [drive](https://drive.google.com/drive/folders/1xQGZUe-i6rTsI_zWq6ntWRqU6QBt9_RN?usp=sharing) link.

