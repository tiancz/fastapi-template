import { Button } from "@chakra-ui/react"
import { useNavigate } from "@tanstack/react-router"
import { FiFolder } from "react-icons/fi"

interface ViewFilesProps {
  id: string
}

const ViewFiles = ({ id }: ViewFilesProps) => {
  const navigate = useNavigate()

  const handleClick = () => {
    navigate({ to: "/kb/$id/docs", params: { id } })
  }

  return (
    <Button
      variant="ghost"
      justifyContent="flex-start"
      onClick={handleClick}
      leftIcon={<FiFolder />}
    >
      View Files
    </Button>
  )
}

export default ViewFiles
