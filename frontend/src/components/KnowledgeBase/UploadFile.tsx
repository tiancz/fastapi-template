
import {
  Button,
  VStack,
} from "@chakra-ui/react"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "@/components/ui/dialog"
import { useDisclosure } from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import { useRef } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { FiUpload } from "react-icons/fi"

import { DocsService } from "@/client"

interface UploadFileProps {
  kbId: string
  isOpen: boolean
  onClose: () => void
}

export const UploadFile = ({ kbId, isOpen, onClose }: UploadFileProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 上传文件的mutation
  const uploadFileMutation = useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData()
      formData.append("file", file)

      return fetch(`/api/v1/kb/${kbId}/docs/upload`, {
        method: "POST",
        body: formData,
      })
    },
    onSuccess: () => {
      showSuccessToast("文件上传成功")
      // 刷新文件列表
      queryClient.invalidateQueries({ queryKey: ["knowledgeBaseFiles", kbId] })
      onClose()
    },
    onError: (error) => {
      showErrorToast(`文件上传失败: ${error.message}`)
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      uploadFileMutation.mutate(file)
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <DialogRoot open={isOpen} onOpenChange={(e) => onClose(e.open)}>
      <DialogContent>
        <DialogHeader>上传文件</DialogHeader>
        <DialogCloseTrigger />
        <DialogBody>
          <VStack spacing={4}>
            <Button
              leftIcon={<FiUpload />}
              colorScheme="blue"
              onClick={handleUploadClick}
              isLoading={uploadFileMutation.isPending}
            >
              选择文件
            </Button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: "none" }}
              accept=".pdf,.doc,.docx,.txt,.md"
            />
          </VStack>
        </DialogBody>
        <DialogFooter>
          <DialogActionTrigger asChild>
            <Button variant="subtle">
              取消
            </Button>
          </DialogActionTrigger>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}
