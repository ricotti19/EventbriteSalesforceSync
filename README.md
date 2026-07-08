# The Source of Hope - Data Integration & Automation Pipeline

This repository contains the backend automation pipeline and data migration framework designed for **The Source of Hope** organization. It streamlines volunteer onboarding, historical record tracking, and real-time database syncing between event platforms and Salesforce CRM.

---

## 🚀 System Architecture & Features

### 1. Real-Time Eventbrite Integration
* **Dynamic Webhook Listener:** A Flask application hosted on Render that actively listens for incoming Eventbrite registration payload events.
* **Two-Way Data Parsing:** Upon receiving an event, the pipeline securely queries the Eventbrite API to extract real-time attendee names and email addresses, eliminating generic placeholders.
* **Automated Lead Creation:** Instantly maps and pushes validated registration details into Salesforce as active Leads under a designated operational category.

### 2. Historical Data Migrations
* **Constant Contact Import:** Successfully migrated extensive historical contact databases from Constant Contact into Salesforce, preserving communication histories and clean records.
* **Volunteer Logs:** Consolidated and imported all historical Eventbrite volunteer attendance logs into Salesforce to maintain accurate tracking of community impact hours.

---

## 🛠️ Technology Stack

* **Backend Framework:** Python / Flask
* **Deployment Platform:** Render (Hosted securely via Private Repository)
* **CRM Platform:** Salesforce (Using REST API wrapper via `simple-salesforce`)
* **Source Systems:** Eventbrite API, Constant Contact Data Export

Note: CSVs hidden
---
