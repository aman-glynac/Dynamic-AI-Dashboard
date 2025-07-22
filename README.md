AI Dashboard Platform - Frontend
A modern, AI-powered dashboard builder that enables users to create interactive data visualizations through natural language prompts. Built with Next.js 14, TypeScript, and Tailwind CSS.
🚀 Features

AI-Powered Chart Generation: Create charts using natural language prompts
Interactive Grid Layout: Drag-and-resize containers with automatic layout management
Real-time Data: Live data updates with WebSocket integration
Multiple Chart Types: Bar, line, pie, scatter plots, and data tables
Edit/View Modes: Seamless switching between editing and presentation modes
Responsive Design: Optimized for desktop and tablet devices
TypeScript: Full type safety throughout the application
Modern UI: Built with shadcn/ui and Tailwind CSS

🛠 Technology Stack
Frontend Architecture

Framework: Next.js 14+ with App Router
UI Library: React 18+ with TypeScript
Styling: Tailwind CSS + shadcn/ui components
State Management: Zustand + TanStack Query (React Query)
Data Visualization: Recharts (primary) + D3.js (custom charts)

Key Dependencies

Next.js 14 - React framework with App Router
React 18 - UI library with concurrent features
TypeScript 5 - Type-safe development
Zustand - Lightweight state management
TanStack Query - Server state management
Recharts - Chart visualization library
Tailwind CSS - Utility-first CSS framework
Radix UI - Accessible component primitives
React Grid Layout - Draggable grid system
Socket.IO Client - Real-time communication

📁 Project Structure
ai-dashboard-frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   └── dashboard/          # Dashboard pages
│   │
│   ├── components/             # React components
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── dashboard/          # Dashboard-specific components
│   │   ├── charts/             # Chart components
│   │   ├── layout/             # Layout components
│   │   └── common/             # Shared components
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useWebSocket.ts     # WebSocket connection
│   │   ├── useDashboard.ts     # Dashboard state
│   │   ├── useChartGeneration.ts # AI chart generation
│   │   └── useRealTimeData.ts  # Real-time data fetching
│   │
│   ├── store/                  # Zustand state stores
│   │   ├── dashboardStore.ts   # Dashboard state
│   │   ├── chartStore.ts       # Chart management
│   │   ├── uiStore.ts          # UI state
│   │   └── dataStore.ts        # Data sources
│   │
│   ├── types/                  # TypeScript type definitions
│   │   ├── dashboard.ts        # Dashboard types
│   │   ├── chart.ts            # Chart types
│   │   ├── container.ts        # Container types
│   │   └── common.ts           # Shared types
│   │
│   ├── services/               # API and external services
│   │   ├── aiService.ts        # AI integration
│   │   ├── dataService.ts      # Data fetching
│   │   └── dashboardService.ts # Dashboard API
│   │
│   └── lib/                    # Utility functions
│       ├── utils.ts            # Common utilities
│       ├── constants.ts        # App constants
│       └── api.ts              # API client
│
├── public/                     # Static assets
├── docs/                       # Documentation
└── tests/                      # Test files
🚀 Getting Started
Prerequisites

Node.js 18.0.0 or later
npm 9.0.0 or later
Git

Installation

Clone the repository
bashgit clone <repository-url>
cd ai-dashboard-frontend

Install dependencies
bashnpm install

Set up environment variables
bashcp .env.local.example .env.local
Update .env.local with your configuration:
envNEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NODE_ENV=development

Install shadcn/ui components
bashnpx shadcn-ui@latest init

Start the development server
bashnpm run dev

Open your browser
Navigate to http://localhost:3000

📖 Usage Guide
Creating Your First Dashboard

Start with a New Dashboard

The app automatically creates a default dashboard on first load
Or click "New" to create a fresh dashboard


Select Container Count

Use the container selector to choose 1-10 containers
Containers automatically arrange in a grid layout


Generate Charts with AI

Click on a container to select it
Type a natural language prompt in the input bar
Examples:

"Create a bar chart showing monthly sales data"
"Show user growth over time as a line chart"
"Display revenue by region in a pie chart"




Customize and Interact

Drag containers to rearrange
Resize containers by dragging corners
Switch between Edit and View modes



Available Chart Types

Bar Chart: Perfect for comparing categories
Line Chart: Ideal for showing trends over time
Pie Chart: Great for showing proportions
Scatter Plot: Useful for correlation analysis
Data Table: Best for detailed data examination

Natural Language Examples
The AI understands various prompt formats:
General Format:
- "Create a [chart type] showing [data description]"
- "Generate a [chart type] for [data context]"
- "Show [data] as a [chart type]"

Specific Examples:
- "Create a bar chart showing quarterly revenue"
- "Line chart of user signups over the last 6 months"
- "Pie chart breaking down traffic sources"
- "Scatter plot of price vs performance metrics"
- "Table showing top 10 products by sales"

With Container Targeting:
- "Put a bar chart in container 3 showing sales data"
- "Create a line chart in the top left showing growth"
🎨 Customization
Theming
The app uses CSS custom properties for theming. Modify globals.css to customize colors:
css:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96%;
  /* Add your custom colors */
}
Adding Chart Types

Create a new chart component in src/components/charts/
Add the type to src/types/chart.ts
Update the chart renderer in ChartRenderer.tsx

Custom Data Sources
Extend the dataService.ts to add new data source types:
typescript// Add to DataSourceConfig type
type: 'api' | 'database' | 'file' | 'your-custom-type'

// Implement in dataService.ts
private async fetchFromCustomSource(dataSource: DataSourceConfig) {
  // Your implementation
}
🧪 Development
Available Scripts

npm run dev - Start development server
npm run build - Build for production
npm run start - Start production server
npm run lint - Run ESLint
npm run type-check - Run TypeScript checks
npm test - Run tests

Code Structure Guidelines

Components: Keep components small and focused
Hooks: Extract complex logic into custom hooks
Types: Define comprehensive TypeScript types
State: Use Zustand for client state, TanStack Query for server state
Styling: Use Tailwind classes, create custom components for reusability

Adding New Features

Create Types: Define TypeScript interfaces first
Add Store Logic: Update Zustand stores if needed
Create Components: Build UI components
Add Service Integration: Connect to backend APIs
Write Tests: Add component and integration tests

📚 Key Components
Dashboard Components

DashboardCanvas - Main dashboard container
DashboardGrid - Grid layout manager
DashboardContainer - Individual container component
PromptInput - Natural language input interface

Chart Components

ChartRenderer - Main chart rendering logic
BarChart, LineChart, PieChart - Specific chart types
DataTable - Tabular data display
EmptyChart - Empty state component

Core Hooks

useChartGeneration - AI-powered chart creation
useRealTimeData - Live data fetching and updates
useWebSocket - Real-time communication
useDashboard - Dashboard state management

🚀 Deployment
Build for Production
bashnpm run build
npm run start
Environment Variables
Ensure these are set in production:
envNEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_WS_URL=wss://your-websocket-domain.com
NODE_ENV=production
Docker Deployment
dockerfileFROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
🤝 Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

Code Style

Use TypeScript for all new code
Follow ESLint configuration
Use Prettier for formatting
Write descriptive commit messages
Add tests for new features

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
🆘 Support

Documentation: Check the /docs folder for detailed guides
Issues: Report bugs and feature requests on GitHub Issues
Discussions: Join community discussions on GitHub Discussions

🗺 Roadmap

 Advanced chart customization
 Multiple dashboard templates
 Collaborative editing
 Advanced data source integrations
 Mobile responsive design
 Export to PDF/PNG
 Dashboard sharing and embedding
 Advanced AI prompt understanding

📊 Performance
The application is optimized for performance with:

Code Splitting: Automatic route-based splitting
Lazy Loading: Chart components loaded on demand
State Management: Efficient state updates with Zustand
Caching: TanStack Query for intelligent data caching
Real-time: Optimized WebSocket connections


Built with ❤️ using Next.js, TypeScript, and AI