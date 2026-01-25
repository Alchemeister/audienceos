interface ProductLayoutProps {
  children: React.ReactNode
  params: Promise<{ id: string }>
}

export default async function ProductLayout({
  children,
}: ProductLayoutProps) {
  // Just pass through children - the dashboard layout handles header/sidebar
  return <>{children}</>
}
