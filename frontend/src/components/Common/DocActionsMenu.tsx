import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

import type { DocPublic } from "@/client"
import DeleteDoc from "../Docs/DeleteDoc"
import EditDoc from "../Docs/EditDoc"

interface DocActionsMenuProps {
  item: DocPublic
}

export const DocActionsMenu = ({ item }: DocActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditDoc item={item} />
        <DeleteDoc id={item.id} />
      </MenuContent>
    </MenuRoot>
  )
}
