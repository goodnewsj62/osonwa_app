from django.db import models


class UserReaction(models.Model):
    user = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s",
        related_query_name="%(app_label)s_%(class)s",
    )
    reaction = models.JSONField(default=dict)

    class Meta:
        abstract = True

    @property
    def reactions(self):
        return self.reaction

    @reactions.setter
    def reactions(self, data):
        if not isinstance(data, dict):
            raise ValueError("must be a mapping")

        existing_reactions = self.reaction
        incoming_reactions = data.keys()

        for reaction in incoming_reactions:
            existing_reactions[reaction] = existing_reactions.get(reaction, 0) + 1

        self.reaction = existing_reactions


# check if data is instance of str if it is get existing reaction and loads incoming reactions
# then add all incoming reactions to existing reaction then set reaction and save return the saved reasctions
