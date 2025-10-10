
import {
  Box,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Button,
  Container,
  Flex,
  Heading,
  Table,
  VStack,
  useDisclosure,
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { FiFile, FiPlus, FiTrash2, FiUpload, FiEye, FiEdit2 } from "react-icons/fi"
import { z } from "zod"

import { KnowledgeBaseService, DocsService } from "@/client"
import { DeleteKnowledgeBase } from "@/components/KnowledgeBase/DeleteKnowledgeBase"
import { KnowledgeBaseActionsMenu } from "@/components/Common/KnowledgeBaseActionsMenu"
import PendingItems from "@/components/Pending/PendingItems"
import { UploadFile } from "@/components/KnowledgeBase/UploadFile"
import { FileDetail } from "@/components/KnowledgeBase/FileDetail"
import { DocPublic } from "@/client"

const knowledgeBaseDetailSchema = z.object({
  id: z.string(),
})

export const Route = createFileRoute("/_layout/knowledgeBaseDetail")({
  component: KnowledgeBaseDetail,
  validateSearch: (search) => knowledgeBaseDetailSchema.parse(search),
})

function KnowledgeBaseDetail() {
  const { id } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // 文件上传模态框状态
  const { isOpen: isUploadOpen, onOpen: onUploadOpen, onClose: onUploadClose } = useDisclosure()

  // 文件详情模态框状态
  const { isOpen: isDetailOpen, onOpen: onDetailOpen, onClose: onDetailClose } = useDisclosure()

  // 当前选中的文件
  const [selectedFile, setSelectedFile] = useState<DocPublic | null>(null)

  // 获取知识库详情
  const { data: knowledgeBase, isLoading: isKnowledgeBaseLoading } = useQuery({
    queryFn: () => KnowledgeBaseService.readKnowledgeBase({ id }),
    queryKey: ["knowledgeBase", id],
  })

  // 获取文件列表
  const { data: files, isLoading: isFilesLoading } = useQuery({
    queryFn: () => KnowledgeBaseService.getKnowledgeBaseFiles({ id }),
    queryKey: ["knowledgeBaseFiles", id],
  })

  // 删除文件的mutation
  const deleteFileMutation = useMutation({
    mutationFn: (fileId: string) => 
      DocsService.deleteDoc({ id: fileId, kbId: id }),
    onSuccess: () => {
      showSuccessToast("文件删除成功")
      // 刷新文件列表
      queryClient.invalidateQueries({ queryKey: ["knowledgeBaseFiles", id] })
    },
    onError: (error) => {
      showErrorToast(`文件删除失败: ${error.message}`)
    },
  })

  // 删除文件处理函数
  const handleDeleteFile = (fileId: string) => {
    deleteFileMutation.mutate(fileId)
  }

  // 上传文件处理函数
  const handleUploadFile = () => {
    onUploadOpen()
  }

  // 查看文件详情处理函数
  const handleViewFile = (file: DocPublic) => {
    setSelectedFile(file)
    onDetailOpen()
  }

  // 编辑文件处理函数
  const handleEditFile = (fileId: string) => {
    // 查找文件详情
    const file = files?.data?.find(f => f.id === fileId)
    if (file) {
      setSelectedFile(file)
      onDetailOpen()
    }
  }

  // 返回知识库列表
  const handleBack = () => {
    navigate({ to: "/knowledgeBase" })
  }

  if (isKnowledgeBaseLoading) {
    return <PendingItems />
  }

  if (!knowledgeBase) {
    return (
      <Container maxW="full">
        <Heading size="lg" pt={12}>
          知识库未找到
        </Heading>
        <Button mt={4} onClick={handleBack}>
          返回知识库列表
        </Button>
      </Container>
    )
  }

  return (
    <Container maxW="full">
      <Breadcrumb pt={6} separator="/">
        <BreadcrumbItem>
          <BreadcrumbLink onClick={handleBack}>知识库管理</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>
          <BreadcrumbLink>{knowledgeBase.name}</BreadcrumbLink>
        </BreadcrumbItem>
      </Breadcrumb>

      <Flex justifyContent="space-between" alignItems="center" mt={6}>
        <VStack align="start">
          <Heading size="lg">{knowledgeBase.name}</Heading>
          {knowledgeBase.description && (
            <Box color="gray.600">{knowledgeBase.description}</Box>
          )}
        </VStack>

        <Flex>
          <KnowledgeBaseActionsMenu item={knowledgeBase} />
        </Flex>
      </Flex>

      <Box mt={8}>
        <Flex justifyContent="space-between" alignItems="center" mb={4}>
          <Heading size="md">文件列表</Heading>
          <Button leftIcon={<FiPlus />} colorScheme="blue" onClick={handleUploadFile}>
            上传文件
          </Button>
        </Flex>

        {isFilesLoading ? (
          <PendingItems />
        ) : (
          <Table.Root size={{ base: "sm", md: "md" }}>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader w="sm">文件名</Table.ColumnHeader>
                <Table.ColumnHeader w="sm">创建者</Table.ColumnHeader>
                <Table.ColumnHeader w="sm">状态</Table.ColumnHeader>
                <Table.ColumnHeader w="sm">操作</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {files?.data?.map((file) => (
                <Table.Row key={file.id}>
                  <Table.Cell>
                    <Flex align="center">
                      <FiFile mr={2} />
                      {file.name}
                    </Flex>
                  </Table.Cell>
                  <Table.Cell>{file.create_by}</Table.Cell>
                  <Table.Cell>
                    <Box
                      px={2}
                      py={1}
                      borderRadius="md"
                      bg={file.status === 1 ? "green.100" : "yellow.100"}
                      color={file.status === 1 ? "green.800" : "yellow.800"}
                    >
                      {file.status === 1 ? "已处理" : "处理中"}
                    </Box>
                  </Table.Cell>
                  <Table.Cell>
                    <Flex>
                      <Button
                        variant="ghost"
                        size="sm"
                        mr={2}
                        onClick={() => handleViewFile(file)}
                      >
                        <FiEye />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        mr={2}
                        onClick={() => handleEditFile(file.id)}
                      >
                        <FiEdit2 />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        colorScheme="red"
                        onClick={() => handleDeleteFile(file.id)}
                        isLoading={deleteFileMutation.isPending}
                      >
                        <FiTrash2 />
                      </Button>
                    </Flex>
                  </Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table.Root>
        )}
      </Box>

      {/* 文件上传模态框 */}
      <UploadFile
        kbId={id}
        isOpen={isUploadOpen}
        onClose={onUploadClose}
      />

      {/* 文件详情模态框 */}
      {selectedFile && (
        <FileDetail
          file={selectedFile}
          isOpen={isDetailOpen}
          onClose={onDetailClose}
        />
      )}
    </Container>
  )
}
