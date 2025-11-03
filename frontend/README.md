This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

# Need to
- translate taiolored resume from latex into something readable
- improve ATS score
- get better keywords

## pages
Page	Route	Purpose
Main Page	/	Core workflow: upload resume + job description, generate tailored resume, display results
Login Page	/login	Handles user authentication (via Supabase, Firebase, or Auth.js)
Saved Resumes Page	/saved	Displays user’s saved tailored resumes (list view with edit/delete options)
Resume Editor Page (optional later)	/edit/[id]	Allows editing of a saved resume in detail view with preview & re-tailoring

## components
UploadForm.tsx	Main Page	Upload resume file and/or paste job description
ATSScoreDisplay.tsx	Main Page	Displays ATS score visually (bar or donut chart)
TailoredResumeEditor.tsx	Main Page / Edit Page	Shows rewritten resume (editable text area or formatted view)
KeywordList.tsx	Main Page	Displays extracted keywords as colored tags
Navbar.tsx	All Pages	Navigation links (Home, Saved, Login, etc.)
Footer.tsx	All Pages	Small footer with credits / version info
PDFExportButton.tsx	Main & Edit Pages	Allows downloading resume as formatted PDF
LoadingSpinner.tsx	All Pages	Reusable spinner for async tasks
Toast.tsx (optional)	All Pages	Small notification system for errors/success messages
AuthForm.tsx	Login Page	Handles login/register inputs and calls auth service
SavedResumeCard.tsx	Saved Page	Displays each saved resume preview (title, date, ATS score, etc.)
ResumePreview.tsx	Edit Page	Renders formatted LaTeX → HTML preview (read-only view)

## lib utilities
api.ts	Axios client (already done)
auth.ts	Handles login/register/logout with Supabase or Firebase
pdf.ts	Utility for generating/exporting PDF from HTML
latexParser.ts	Converts LaTeX string → readable HTML/Markdown
storage.ts	Handles saving/loading resumes (localStorage or Supabase)
constants.ts	Holds app-wide constants like API base URL, color theme, etc.