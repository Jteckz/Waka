from django.utils import timezone


class SoftDeleteQuerySetMixin:
    def delete(self):
        self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def all_with_deleted(self):
        return self.filter()
