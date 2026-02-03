# Sidebar Navigation

This application now includes a responsive sidebar navigation built with Tailwind CSS.

## Features

- **Collapsible Sidebar**: The sidebar can be collapsed to save screen space
- **Active Page Highlighting**: The current page is highlighted in the sidebar
- **RTL Support**: The sidebar supports right-to-left layout for Persian language
- **Responsive Design**: Works well on different screen sizes

## Navigation Items

1. **خانه (Home)**: The main landing page with welcome message
2. **داشبوردهای Superset (Superset Dashboards)**: List of available Superset dashboards
3. **داشبورد بوشهر (Bushehr Dashboard)**: The Bushehr province dashboard

## How to Use

1. Click on any item in the sidebar to navigate to that page
2. Use the arrow button at the top of the sidebar to collapse/expand it
3. The active page is highlighted with a blue background

## Technical Implementation

- The sidebar is implemented as a React component (`src/components/Sidebar.tsx`)
- It uses React Router for navigation
- Tailwind CSS is used for styling
- The layout is managed by the `Layout` component (`src/components/Layout.tsx`)

## Customization

To add new navigation items, edit the `sidebarItems` array in `src/components/Sidebar.tsx`:

```typescript
const sidebarItems: SidebarItem[] = [
  // ... existing items
  {
    id: 'new-page',
    name: 'صفحه جدید',
    icon: <YourIconComponent />,
    path: '/new-page'
  }
];
```

Don't forget to add the corresponding route in `src/App.tsx`.