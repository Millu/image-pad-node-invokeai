import os
from PIL import Image
from invokeai.app.invocations.baseinvocation import (
    BaseInvocation,
    Input,
    InvocationContext,
    invocation,
    InputField,
    WithMetadata,
    WithWorkflow,
)
from invokeai.app.invocations.primitives import ImageField, ImageOutput
from invokeai.app.services.image_records.image_records_common import (
    ImageCategory,
    ResourceOrigin,
)

@invocation(
    "Pad_Image",
    title="Pad Image",
    tags=["image", "padding"],
    category="image",
    version="1.0.0",
    use_cache=False,
)
class PadImageInvocation(BaseInvocation, WithMetadata, WithWorkflow):
    """Pad an Image"""

    input_image: ImageField = InputField(
        description="Input image to pad"
    )
    x_offset: int = InputField(
        default=0, description="X offset for padding"
    )
    y_offset: int = InputField(
        default=0, description="Y offset for padding"
    )
    padding_color: tuple = InputField(
        default=(0, 0, 0), description="Padding color as RGB tuple"
    )

    def pad_image(self, input_image: Image.Image, x_offset: int, y_offset: int, padding_color: tuple) -> Image.Image:
        width, height = input_image.size
        new_width = width + 2 * x_offset
        new_height = height + 2 * y_offset

        padded_image = Image.new("RGB", (new_width, new_height), padding_color)
        padded_image.paste(input_image, (x_offset, y_offset))

        return padded_image

    def invoke(self, context: InvocationContext) -> ImageOutput:
        input_image = context.services.images.get_pil_image(self.input_image.image_name)

        padded_image = self.pad_image(input_image, self.x_offset, self.y_offset, self.padding_color)

        padded_image_dto = context.services.images.create(
            image=padded_image,
            image_origin=ResourceOrigin.INTERNAL,
            image_category=ImageCategory.GENERAL,
            board_id=None,
            node_id=self.id,
            session_id=context.graph_execution_state_id,
            is_intermediate=self.is_intermediate,
            metadata=self.metadata,
            workflow=self.workflow,
        )

        return ImageOutput(
            image=ImageField(image_name=padded_image_dto.image_name),
            width=padded_image_dto.width,
            height=padded_image_dto.height,
        )
