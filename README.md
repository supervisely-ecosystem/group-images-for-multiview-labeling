<div align="center" markdown>
<img src="https://github.com/supervisely-ecosystem/group-images-for-multiview-labeling/assets/115161827/1ffcc28f-a466-4036-a909-95aceedebb7e"/>  

# Group Images for Multiview Labeling

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> 
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/group-images-for-multiview)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/group-images-for-multiview)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/group-images-for-multiview)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/group-images-for-multiview)](https://supervise.ly)

</div>

# Overview

The application organizes images into groups, adds grouping tags, and activates grouping and multi-tag modes in the project settings. The size of the groups is determined by the **Batch size** slider in the application window, and three grouping options are available: **Group by Batches**, **Group by Object Class**, and **Group by Image Tags**.

**Group by Batches**: Randomly divides the images into groups, affecting each image.

**Group by Object Class**: Categorizes images into groups based on the objects' classes present in them. It does not impact images with no objects.

**Group by Image Tags**: Organizes images into groups based on their tags. Images without tags remain unaffected.

Before runnning the app, be aware that it alters the applied project. All application actions can be manually reversed in the project settings, but it is advisable to create a project copy if you are concerned about impact this app may have on the project. 

Additionally, you can enable synchronized panning and labeling for use with the multiview. This can be configured in the project settings under the visuals category:

<img src="https://github.com/supervisely-ecosystem/group-images-for-multiview-labeling/assets/115161827/e27a319a-9371-4daa-87c4-0c6a9e5bebc0" width = 50%>


# How to Run

1. Go to your Workspace

2. Right click to the project/dataset and run app from context menu

<img src="https://github.com/supervisely-ecosystem/group-images-for-multiview-labeling/assets/115161827/5287e318-ddb1-4e5a-b65e-15ebe9a6dbaf">

3. Select the grouping type, batch size and run the app.

<img src="https://github.com/supervisely-ecosystem/group-images-for-multiview-labeling/assets/115161827/719a9344-d6eb-4d09-b943-04df129c432a">

## Result

Here is how the result looks like in the labeling toolbox:

<img src="https://github.com/supervisely-ecosystem/group-images-for-multiview-labeling/assets/115161827/6f6c9cd6-a8c8-4c08-8787-fb7c34a30d95">
