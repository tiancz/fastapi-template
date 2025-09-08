import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  VStack,
  HStack,
  Icon,
  Spinner,
} from "@chakra-ui/react"
import { FiArrowLeft, FiFile, FiFolder } from "react-icons/fi"

import { KnowledgeBaseService } from "@/client"

const DocumentList = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [knowledgeBaseName, setKnowledgeBaseName] = useState("")

  // 获取知识库中的文件列表
  const { data: files, isLoading } = useQuery({
    queryKey: ["docs", id],
    queryFn: () => KnowledgeBaseService.getKnowledgeBaseFiles({ id: id! }),
    enabled: !!id,
  })

  // 获取知识库详情以显示名称
  const { data: knowledgeBase } = useQuery({
    queryKey: ["knowledgeBase", id],
    queryFn: () => KnowledgeBaseService.readKnowledgeBase({ id: id! }),
    enabled: !!id,
  })

  useEffect(() => {
    if (knowledgeBase) {
      setKnowledgeBaseName(knowledgeBase.name)
    }
  }, [knowledgeBase])

  return (
    <Box p={4}>
      <HStack mb={6}>
        <Button
          leftIcon={<Icon as={FiArrowLeft} />}
          onClick={() => navigate(-1)}
          variant="ghost"
        >
          Back
        </Button>
        <Heading size="lg">Files in "{knowledgeBaseName}"</Heading>
      </HStack>

      {isLoading ? (
        <Spinner />
      ) : (
        <VStack align="stretch" spacing={4}>
          {files && files.length > 0 ? (
            files.map((file) => (
              <Card key={file.id} variant="outline">
                <CardHeader>
                  <HStack>
                    <Icon as={file.type === "folder" ? FiFolder : FiFile} />
                    <Text fontWeight="bold">{file.name}</Text>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <Text fontSize="sm" color="gray.500">
                    {file.description || "No description"}
                  </Text>
                </CardBody>
              </Card>
            ))
          ) : (
            <Text>No files found in this knowledge base.</Text>
          )}
        </VStack>
      )}
    </Box>
  )
}

export default DocumentList
