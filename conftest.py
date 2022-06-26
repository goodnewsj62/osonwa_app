from pytest_factoryboy import register

from account.factories import (
    UserFactory,
    NotificationFactory,
    ProfileFactory,
    SocialAccountFactory,
)


factories_ = [
    (UserFactory, "user"),
    (NotificationFactory, "notification"),
    (ProfileFactory, "profile"),
    (SocialAccountFactory, "social"),
]


for factory in factories_:
    register(
        factory[0]
    )  # factories needed globally by other factories defining subfactory from them

    register(factory[0], f"{factory[1]}_a")
