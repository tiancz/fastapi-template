
import {
  Button,
  VStack,
  Heading,
  Text,
  Box,
} from "@chakra-ui/react"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { FiEye, FiDownload, FiEdit2 } from "react-icons/fi"

import { DocsService, DocPublic } from "@/client"

interface FileDetailProps {
  file: DocPublic
  isOpen: boolean
  onClose: () => void
}

export const FileDetail = ({ file, isOpen, onClose }: FileDetailProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [content, setContent] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // 获取文件内容的mutation
  const getFileContentMutation = useMutation({
    mutationFn: () => 
      fetch(`/api/v1/kb/${file.kbId}/docs/${file.id}/content`)
        .then(res => res.text()),
    onSuccess: (data) => {
      setContent(data)
    },
    onError: (error) => {
      showErrorToast(`获取文件内容失败: ${error.message}`)
    },
  })

  // 下载文件的mutation
  const downloadFileMutation = useMutation({
    mutationFn: () => 
      fetch(`/api/v1/kb/${file.kbId}/docs/${file.id}/download`)
        .then(res => res.blob()),
    onSuccess: (blob) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    },
    onError: (error) => {
      showErrorToast(`下载文件失败: ${error.message}`)
    },
  })

  // 更新文件内容的mutation
  const updateFileContentMutation = useMutation({
    mutationFn: (newContent: string) => 
      fetch(`/api/v1/kb/${file.kbId}/docs/${file.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: file.name, content: newContent }),
      }),
    onSuccess: () => {
      showSuccessToast("文件更新成功")
      // 刷新文件列表
      queryClient.invalidateQueries({ queryKey: ["knowledgeBaseFiles", file.kbId] })
      onClose()
    },
    onError: (error) => {
      showErrorToast(`文件更新失败: ${error.message}`)
    },
  })

  const handleViewContent = () => {
    setIsLoading(true)
    getFileContentMutation.mutate()
    setIsLoading(false)
  }

  const handleDownload = () => {
    downloadFileMutation.mutate()
  }

  const handleEdit = () => {
    // 这里应该打开编辑模态框
    showErrorToast("文件编辑功能开发中")
  }

  return (
    <DialogRoot open={isOpen} onOpenChange={(e) => onClose(e.open)}>
      <DialogContent>
        <DialogHeader>文件详情</DialogHeader>
        <DialogCloseTrigger />
        <DialogBody>
          <VStack spacing={4} align="start">
            <Box>
              <Heading size="sm" mb={2}>文件信息</Heading>
              <Text><strong>文件名:</strong> {file.name}</Text>
              <Text><strong>创建者:</strong> {file.create_by}</Text>
              <Text><strong>状态:</strong> 
                <Box
                  as="span"
                  ml={2}
                  px={2}
                  py={1}
                  borderRadius="md"
                  bg={file.status === 1 ? "green.100" : "yellow.100"}
                  color={file.status === 1 ? "green.800" : "yellow.800"}
                >
                  {file.status === 1 ? "已处理" : "处理中"}
                </Box>
              </Text>
            </Box>

            <Box>
              <Heading size="sm" mb={2}>文件内容</Heading>
              {content ? (
                <Box
                  p={4}
                  bg="gray.100"
                  borderRadius="md"
                  whiteSpace="pre-wrap"
                  maxH="300px"
                  overflowY="auto"
                >
                  {content}
                </Box>
              ) : (
                <Text color="gray.500">点击查看按钮获取文件内容</Text>
              )}
            </Box>
          </VStack>
        </DialogBody>
        <DialogFooter>
          <DialogActionTrigger asChild>
            <Button variant="subtle" mr={2}>
              关闭
            </Button>
          </DialogActionTrigger>
          <Button
            leftIcon={<FiEye />}
            onClick={handleViewContent}
            isLoading={getFileContentMutation.isPending}
            mr={2}
          >
            查看内容
          </Button>
          <Button
            leftIcon={<FiDownload />}
            onClick={handleDownload}
            isLoading={downloadFileMutation.isPending}
            mr={2}
          >
            下载
          </Button>
          <Button
            leftIcon={<FiEdit2 />}
            onClick={handleEdit}
            isLoading={updateFileContentMutation.isPending}
            colorScheme="blue"
          >
            编辑
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}
