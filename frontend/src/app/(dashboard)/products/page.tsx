"use client"

import { useAuthToken } from "@/hooks/use-auth-token"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Package, Plus } from "lucide-react"

import { api } from "@/lib/api"
import type { Product, ProductCreate } from "@/lib/types"
import { ProductCard } from "@/components/products/product-card"
import { CreateProductDialog } from "@/components/products/create-product-dialog"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"

export default function ProductsPage() {
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const token = await getToken()
      return api.products.list(token)
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: ProductCreate) => {
      const token = await getToken()
      return api.products.create(token, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] })
      toast({
        title: "Product created",
        description: "Your product has been created successfully.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to create product. Please try again.",
        variant: "destructive",
      })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const token = await getToken()
      return api.products.delete(token, id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] })
      toast({
        title: "Product deleted",
        description: "Your product has been deleted successfully.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to delete product. Please try again.",
        variant: "destructive",
      })
    },
  })

  const handleCreate = async (data: ProductCreate) => {
    await createMutation.mutateAsync(data)
  }

  const handleDelete = (product: Product) => {
    if (confirm(`Are you sure you want to delete "${product.name}"? This action cannot be undone.`)) {
      deleteMutation.mutate(product.id)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-64 mt-2" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
        <p className="text-destructive">Failed to load products</p>
        <Button onClick={() => queryClient.invalidateQueries({ queryKey: ["products"] })}>
          Try Again
        </Button>
      </div>
    )
  }

  const products = data?.items || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Products</h1>
          <p className="text-muted-foreground">
            Manage your products and track feedback across channels.
          </p>
        </div>
        <CreateProductDialog onSubmit={handleCreate} />
      </div>

      {/* Products grid */}
      {products.length === 0 ? (
        <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
          <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
            <Package className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="font-semibold mb-2">No products yet</h3>
          <p className="text-muted-foreground mb-4 max-w-sm">
            Create your first product to start tracking feedback and discovering
            where your audience hangs out.
          </p>
          <CreateProductDialog
            onSubmit={handleCreate}
            trigger={
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Product
              </Button>
            }
          />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}
