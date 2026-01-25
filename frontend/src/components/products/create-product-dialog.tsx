"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Loader2, Plus, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"

const productSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().min(1, "Description is required"),
  url: z.string().url("Must be a valid URL").optional().or(z.literal("")),
  keywords: z.array(z.string()).default([]),
  competitors: z.array(z.string()).default([]),
})

type ProductFormValues = z.infer<typeof productSchema>

interface CreateProductDialogProps {
  onSubmit: (data: ProductFormValues) => Promise<void>
  trigger?: React.ReactNode
}

export function CreateProductDialog({ onSubmit, trigger }: CreateProductDialogProps) {
  const [open, setOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [keywordInput, setKeywordInput] = useState("")
  const [competitorInput, setCompetitorInput] = useState("")

  const form = useForm<ProductFormValues>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      name: "",
      description: "",
      url: "",
      keywords: [],
      competitors: [],
    },
  })

  const handleSubmit = async (data: ProductFormValues) => {
    setIsSubmitting(true)
    try {
      await onSubmit({
        ...data,
        url: data.url || undefined,
      })
      setOpen(false)
      form.reset()
    } catch (error) {
      console.error("Failed to create product:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const addKeyword = () => {
    if (keywordInput.trim()) {
      const currentKeywords = form.getValues("keywords")
      if (!currentKeywords.includes(keywordInput.trim())) {
        form.setValue("keywords", [...currentKeywords, keywordInput.trim()])
      }
      setKeywordInput("")
    }
  }

  const removeKeyword = (keyword: string) => {
    const currentKeywords = form.getValues("keywords")
    form.setValue(
      "keywords",
      currentKeywords.filter((k) => k !== keyword)
    )
  }

  const addCompetitor = () => {
    if (competitorInput.trim()) {
      const currentCompetitors = form.getValues("competitors")
      if (!currentCompetitors.includes(competitorInput.trim())) {
        form.setValue("competitors", [...currentCompetitors, competitorInput.trim()])
      }
      setCompetitorInput("")
    }
  }

  const removeCompetitor = (competitor: string) => {
    const currentCompetitors = form.getValues("competitors")
    form.setValue(
      "competitors",
      currentCompetitors.filter((c) => c !== competitor)
    )
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Product
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Create New Product</DialogTitle>
          <DialogDescription>
            Add a new product to start tracking feedback and discovering audiences.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Product Name</FormLabel>
                  <FormControl>
                    <Input placeholder="My Awesome Product" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe your product and target audience..."
                      className="resize-none"
                      rows={3}
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    This helps AI understand your product for better research results.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Website URL (optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="https://myproduct.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="keywords"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Keywords (optional)</FormLabel>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add keyword..."
                      value={keywordInput}
                      onChange={(e) => setKeywordInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault()
                          addKeyword()
                        }
                      }}
                    />
                    <Button type="button" variant="outline" onClick={addKeyword}>
                      Add
                    </Button>
                  </div>
                  {field.value.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {field.value.map((keyword) => (
                        <Badge key={keyword} variant="secondary" className="gap-1">
                          {keyword}
                          <button
                            type="button"
                            onClick={() => removeKeyword(keyword)}
                            className="ml-1 hover:text-destructive"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}
                  <FormDescription>
                    Keywords to monitor for mentions. AI will suggest more after research.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="competitors"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Competitors (optional)</FormLabel>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add competitor..."
                      value={competitorInput}
                      onChange={(e) => setCompetitorInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault()
                          addCompetitor()
                        }
                      }}
                    />
                    <Button type="button" variant="outline" onClick={addCompetitor}>
                      Add
                    </Button>
                  </div>
                  {field.value.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {field.value.map((competitor) => (
                        <Badge key={competitor} variant="outline" className="gap-1">
                          {competitor}
                          <button
                            type="button"
                            onClick={() => removeCompetitor(competitor)}
                            className="ml-1 hover:text-destructive"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create Product
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
