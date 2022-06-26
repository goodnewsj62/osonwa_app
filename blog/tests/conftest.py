from pytest_factoryboy import register

from blog.factories import (
    BundleFactory,
    PostFactory,
    PostImagesFactory,
    PostUserReactionFactory,
)


factories_ = [
    (BundleFactory, "bundle"),
    (PostFactory, "post"),
    (PostImagesFactory, "post_image"),
    (PostUserReactionFactory, "post_user"),
]

for factory in factories_:
    register(
        factory[0]
    )  # factories needed globally by other factories defining subfactory from them
    register(factory[0], f"{factory[1]}_a")
