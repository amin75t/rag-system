c# Router Setup Instructions

This document explains how to set up and run the React Router implementation for the AI Assistant Frontend.

## What's Been Added

1. **React Router DOM**: Added as a dependency for routing functionality
2. **Page Components**: Created separate page components for better code organization
   - `DashboardListPage`: Displays the list of available dashboards
   - `DashboardViewPage`: Shows a specific dashboard based on UUID
3. **Routing Configuration**: Updated `App.tsx` to use BrowserRouter and Route components

## Installation Steps

1. Install the required dependencies:
   ```bash
   cd front-end/ai-assistant-front
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Route Structure

- `/` - Dashboard list page (home page)
- `/dashboard/:dashboardUuid` - Individual dashboard view page
- `/busher` - Busher UI page showing Bushehr province dashboard

## How It Works

1. The main `App.tsx` component now wraps the entire application in a `BrowserRouter`
2. The `Routes` component defines the available routes
3. The `DashboardListPage` shows all available dashboards with clickable links
4. Clicking on a dashboard navigates to the `DashboardViewPage` with the dashboard UUID as a URL parameter
5. The `DashboardViewPage` uses the `useParams` hook to extract the UUID from the URL and display the appropriate dashboard
6. The `BusherUIPage` displays the Bushehr province dashboard with its custom UI components
7. Navigation between different sections is handled through the header navigation links

## Benefits

- **Better URL Management**: Each dashboard has its own URL that can be bookmarked
- **Improved Navigation**: Users can use the browser's back/forward buttons
- **Code Organization**: Separated concerns with dedicated page components
- **Scalability**: Easy to add more routes and pages in the future
- **Multiple UI Systems**: Integrated both Superset dashboard embedding and Busher UI for different data visualization needs