import {
  Container,
  Heading,
  Text,
  Card,
  CardBody,
  VStack,
  HStack,
  Button,
  Icon,
  Spinner,
  EmptyState,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiArrowLeft, FiFile } from "react-icons/fi"

import { KnowledgeBaseService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/knowledgeBase/docs")({
  component: KnowledgeBaseFiles,
})

function KnowledgeBaseFiles() {
  const { id } = Route.useParams()
  const navigate = useNavigate()
  const { showErrorToast } = useCustomToast()

  // 获取知识库信息
  const { data: knowledgeBase, isLoading: isKBLoading } = useQuery({
    queryKey: ["knowledgeBase", id],
    queryFn: () => KnowledgeBaseService.readKnowledgeBase({ id }),
    onError: (error: any) => {
      showErrorToast("Failed to load knowledge base")
      console.error(error)
    }
  })

  // 获取知识库中的文件列表（这里假设有一个获取文件列表的API）
  const { data: files, isLoading: isFilesLoading, isError } = useQuery({
    queryKey: ["knowledgeBaseFiles", id],
    queryFn: () => KnowledgeBaseService.readKnowledgeBase({ id }), // 这里暂时使用readKnowledgeBase作为示例
    enabled: !!id, // 只有当id存在时才执行查询
  })

  if (isKBLoading) {
    return (
      <Container maxW="full" py={8}>
        <Spinner />
      </Container>
    )
  }

  return (
    <Container maxW="full">
      <VStack align="stretch" spacing={6}>
        <HStack>
          <Button
            leftIcon={<Icon as={FiArrowLeft} />}
            onClick={() => navigate({ to: "/_layout/knowledge-bases" })}
            variant="ghost"
          >
            Back
          </Button>
          <Heading size="lg">
            Files in "{knowledgeBase?.name}"
          </Heading>
        </HStack>

        {isFilesLoading ? (
          <Spinner />
        ) : isError ? (
          <EmptyState.Root>
            <EmptyState.Content>
              <EmptyState.Title>Error loading files</EmptyState.Title>
              <EmptyState.Description>
                There was an error loading the files for this knowledge base.
              </EmptyState.Description>
            </EmptyState.Content>
          </EmptyState.Root>
        ) : files ? (
          <VStack align="stretch" spacing={4}>
            {/* 这里显示文件列表 - 你需要根据实际API响应结构调整 */}
            <Card variant="outline">
              <CardBody>
                <HStack>
                  <Icon as={FiFile} />
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">Sample File</Text>
                    <Text fontSize="sm" color="gray.500">
                      This is a sample file in this knowledge base
                    </Text>
                  </VStack>
                </HStack>
              </CardBody>
            </Card>
          </VStack>
        ) : (
          <EmptyState.Root>
            <EmptyState.Content>
              <EmptyState.Title>No files found</EmptyState.Title>
              <EmptyState.Description>
                This knowledge base doesn't contain any files yet.
              </EmptyState.Description>
            </EmptyState.Content>
          </EmptyState.Root>
        )}
      </VStack>
    </Container>
  )
}

export default KnowledgeBaseFiles
