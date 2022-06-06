import json

from django.db import models


class UserReaction(models.Model):
    user = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s",
        related_query_name="%(app_label)s_%(class)s",
    )
    reactions = models.JSONField(default=dict)

    class Meta:
        abstract = True

    def get_reactions(self):
        return json.dumps(self.reactions)

    def set_reactions(self, data):
        if not isinstance(data, str):
            raise ValueError("must be a serialize json string")

        existing_reactions = self.reaction
        incoming_reactions = json.loads(data).keys()

        for reaction in incoming_reactions:
            existing_reactions[reaction] = existing_reactions.get(reaction, 0) + 1

        self.reaction = existing_reactions
        self.save()
        return self.get_reactions()


# check if data is instance of str if it is get existing reaction and loads incoming reactions
# then add all incoming reactions to existing reaction then set reaction and save return the saved reasctions
