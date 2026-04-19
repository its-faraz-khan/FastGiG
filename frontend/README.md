# FairGig Frontend

React 18 + TypeScript frontend for the FairGig platform - an earnings tracking and verification system for gig workers.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Running the App](#running-the-app)
- [Development Guidelines](#development-guidelines)
- [API Integration](#api-integration)
- [Responsive Design](#responsive-design)
- [Internationalization](#internationalization)
- [Testing](#testing)

---

## ✨ Features

- **Multi-Role Authentication**: Worker, Verifier, and Advocate login flows
- **Worker Dashboard**: Earnings summary, charts, and quick analytics
- **Earnings Logger**: Manual entry form and CSV bulk import
- **Screenshot Verification**: Upload and verification workflow
- **Income Certificate**: Generate printable certificates
- **Grievance Board**: Community complaint board with moderation
- **Analytics**: Worker and advocate dashboards with Recharts
- **Bilingual Support**: English and Urdu interface
- **Responsive Design**: Mobile-first, works on 375px+ screens
- **State Management**: React Context + React Query for server state

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | React 18 + TypeScript |
| **Build Tool** | Vite 5+ |
| **Styling** | Tailwind CSS 3+ |
| **Routing** | React Router v6 |
| **Forms** | React Hook Form |
| **HTTP Client** | Axios |
| **State Management** | React Context + React Query |
| **Charts** | Recharts |
| **i18n** | i18next + react-i18next |
| **Code Quality** | ESLint + Prettier |

---

## 📦 Installation

### Prerequisites

- Node.js 16+ and npm 8+
- Git

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd frontend

# Install dependencies
npm install

# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your editor
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8001

# App Configuration
VITE_APP_NAME=FairGig
VITE_APP_VERSION=1.0.0
VITE_ENV=development
```

**Important**: Do NOT commit `.env` to version control. Use `.env.example` as template.

---

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
│   └── index.html         # HTML entry point
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Card.tsx       # To be created
│   ├── pages/             # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   └── ...
│   ├── services/          # API client and services
│   │   ├── apiClient.ts   # Axios instance with interceptors
│   │   └── authService.ts # Authentication logic
│   ├── hooks/             # Custom React hooks
│   │   ├── useAuth.ts     # Auth context hook
│   │   └── useApi.ts      # API call hook
│   ├── context/           # React Context for global state
│   │   └── AuthContext.tsx
│   ├── i18n/              # Internationalization
│   │   ├── config.ts      # i18next configuration
│   │   └── locales/
│   │       ├── en.json    # English translations
│   │       └── ur.json    # Urdu translations
│   ├── types/             # TypeScript type definitions
│   │   └── models.ts      # Data models
│   ├── utils/             # Helper functions
│   │   └── helpers.ts     # Utility functions
│   ├── App.tsx            # Root component
│   ├── index.tsx          # Entry point
│   └── index.css          # Global styles
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
├── .eslintrc.json         # ESLint configuration
├── .prettierrc             # Prettier configuration
├── package.json           # Dependencies
└── README.md              # This file
```

---

## 🚀 Running the App

### Development Mode

```bash
# Start dev server with hot reload
npm run dev

# Open http://localhost:3000 in your browser
```

The app will automatically reload when you save files.

### Production Build

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview
```

### Other Commands

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Formatting with Prettier
npm run format
```

---

## 💻 Development Guidelines

### Component Structure

```typescript
import React from 'react';

interface ComponentProps {
  name: string;
  onAction?: () => void;
}

export const Component: React.FC<ComponentProps> = ({ name, onAction }) => {
  return (
    <div className="...">
      <h1>{name}</h1>
    </div>
  );
};
```

### Styling Rules

- Use Tailwind CSS classes for all styling
- Mobile-first approach (start with mobile, then breakpoints: sm:, md:, lg:, xl:)
- Use custom Tailwind utilities in `src/index.css` for repeated patterns
- Never use inline styles

### TypeScript Best Practices

- Always define types for props
- Use `React.FC<Props>` for functional components
- Import types from `@types` directory
- Use strict mode enabled (check `tsconfig.json`)

### API Integration

```typescript
import { useAuth } from '@hooks/useAuth';
import { useApi } from '@hooks/useApi';

const MyComponent = () => {
  const { token } = useAuth();
  const { data, loading, error, execute } = useApi();

  const fetchData = async () => {
    await execute('get', '/earnings/worker/123');
  };

  return (
    <button onClick={fetchData} disabled={loading}>
      {loading ? 'Loading...' : 'Fetch Data'}
    </button>
  );
};
```

---

## 🌐 API Integration

### Authentication

All API requests automatically include JWT token:

```typescript
// Request headers automatically include:
// Authorization: Bearer <token>
```

### Token Refresh

Tokens are automatically refreshed when expired:

```typescript
// If 401 Unauthorized received, token refresh is attempted automatically
// If refresh fails, user is redirected to login
```

### Error Handling

```typescript
import { getErrorMessage } from '@utils/helpers';
import apiClient from '@services/apiClient';

try {
  const response = await apiClient.get('/data');
} catch (error) {
  const message = getErrorMessage(error);
  console.error(message);
}
```

---

## 📱 Responsive Design

### Breakpoints (Tailwind)

- **Mobile**: <640px (default styles)
- **Tablet**: 640px+ (sm:)
- **Desktop**: 1024px+ (lg:)

### Testing Responsive Design

```bash
# Use browser DevTools to test:
# 375px (mobile) - iPhone SE
# 768px (tablet) - iPad
# 1024px+ (desktop) - Desktop
```

### Mobile-First Example

```tsx
<div className="w-full sm:w-1/2 lg:w-1/3">
  {/* Full width on mobile, 50% on tablet, 33% on desktop */}
</div>
```

---

## 🌍 Internationalization (i18n)

### Switching Language

```typescript
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { i18n, t } = useTranslation();

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  return (
    <div>
      <p>{t('common.welcome')}</p>
      <button onClick={() => changeLanguage('ur')}>Urdu</button>
      <button onClick={() => changeLanguage('en')}>English</button>
    </div>
  );
};
```

### Adding Translations

1. Add key-value pairs to `src/i18n/locales/en.json` and `src/i18n/locales/ur.json`
2. Use in components: `t('path.to.key')`

### Translation Keys

```json
{
  "common": {
    "appName": "FairGig",
    "email": "Email"
  },
  "auth": {
    "login": "Login",
    "register": "Register"
  }
}
```

---

## 🧪 Testing

### Unit Tests (To be configured)

```bash
npm run test
```

### E2E Tests (To be configured)

```bash
npm run test:e2e
```

### Testing Checklist

- [ ] Login/Register flow works
- [ ] Token refresh on 401 errors
- [ ] Language switching (EN/UR)
- [ ] Responsive on mobile/tablet/desktop
- [ ] Form validation displays errors
- [ ] API errors handled gracefully
- [ ] Charts render correctly
- [ ] CSV import works

---

## 🔍 Common Issues

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :3000 | findstr LISTENING  # Windows
```

### Module Not Found

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

```bash
# Run type check
npm run type-check
```

---

## 📖 Useful Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite Guide](https://vitejs.dev/guide/)
- [React Router](https://reactrouter.com)
- [React Hook Form](https://react-hook-form.com)
- [i18next Documentation](https://www.i18next.com)

---

## 🤝 Contributing

Follow these guidelines when contributing:

1. Create feature branches: `git checkout -b feature/your-feature`
2. Write clear commit messages
3. Ensure TypeScript has no errors: `npm run type-check`
4. Format code: Use Prettier integration
5. Test changes before submitting PR

---

## 📄 License

Part of the FairGig platform project.

---

## 🆘 Support

For issues or questions, contact the development team or create an issue in the repository.

---

## 🔄 Next Steps

After completing Phase 1 (Frontend Foundation):

1. **Phase 2**: Create Login and Register pages
2. **Phase 3**: Build Worker Dashboard
3. **Phase 4**: Implement Earnings Logger
4. **Phase 5**: Add Screenshot Upload & Verification
5. **Phase 6**: Generate Income Certificates

See [IMPLEMENTATION_ROADMAP.md](../IMPLEMENTATION_ROADMAP.md) for details.
