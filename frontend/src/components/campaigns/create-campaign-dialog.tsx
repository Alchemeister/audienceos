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

const campaignSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().max(2000).optional(),
  target_subreddits: z.array(z.string()).default([]),
})

type CampaignFormValues = z.infer<typeof campaignSchema>

interface CreateCampaignDialogProps {
  productId: string
  onSubmit: (data: CampaignFormValues & { product_id: string }) => Promise<void>
  trigger?: React.ReactNode
}

export function CreateCampaignDialog({
  productId,
  onSubmit,
  trigger,
}: CreateCampaignDialogProps) {
  const [open, setOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [subredditInput, setSubredditInput] = useState("")

  const form = useForm<CampaignFormValues>({
    resolver: zodResolver(campaignSchema),
    defaultValues: {
      name: "",
      description: "",
      target_subreddits: [],
    },
  })

  const handleSubmit = async (data: CampaignFormValues) => {
    setIsSubmitting(true)
    try {
      await onSubmit({
        ...data,
        product_id: productId,
      })
      setOpen(false)
      form.reset()
    } catch (error) {
      console.error("Failed to create campaign:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const addSubreddit = () => {
    if (subredditInput.trim()) {
      const subreddit = subredditInput.trim().replace(/^r\//, "")
      const currentSubreddits = form.getValues("target_subreddits")
      if (!currentSubreddits.includes(subreddit)) {
        form.setValue("target_subreddits", [...currentSubreddits, subreddit])
      }
      setSubredditInput("")
    }
  }

  const removeSubreddit = (subreddit: string) => {
    const currentSubreddits = form.getValues("target_subreddits")
    form.setValue(
      "target_subreddits",
      currentSubreddits.filter((s) => s !== subreddit)
    )
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Campaign
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create Campaign</DialogTitle>
          <DialogDescription>
            Create a new marketing campaign to reach your audience.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Campaign Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Q1 Reddit Outreach" {...field} />
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
                  <FormLabel>Description (optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Campaign goals and strategy..."
                      className="resize-none"
                      rows={3}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="target_subreddits"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Target Subreddits (optional)</FormLabel>
                  <div className="flex gap-2">
                    <Input
                      placeholder="r/subreddit"
                      value={subredditInput}
                      onChange={(e) => setSubredditInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault()
                          addSubreddit()
                        }
                      }}
                    />
                    <Button type="button" variant="outline" onClick={addSubreddit}>
                      Add
                    </Button>
                  </div>
                  {field.value.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {field.value.map((subreddit) => (
                        <Badge key={subreddit} variant="secondary" className="gap-1">
                          r/{subreddit}
                          <button
                            type="button"
                            onClick={() => removeSubreddit(subreddit)}
                            className="ml-1 hover:text-destructive"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}
                  <FormDescription>
                    Communities discovered in audience research can be added here.
                  </FormDescription>
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
                Create Campaign
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
