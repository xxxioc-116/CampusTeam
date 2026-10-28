from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Application, AuditLog, Invitation, RequestStatus, TeamMember


def audit(actor, action, target, **details):
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target.__class__.__name__,
        target_id=str(target.pk),
        details=details,
    )


@transaction.atomic
def transition_request(instance, action, actor):
    if instance.status != RequestStatus.PENDING:
        raise ValidationError("该记录已处理，不能重复操作")

    if isinstance(instance, Application):
        is_owner = instance.project.owner_id == actor.id
        if action == "withdraw":
            if instance.applicant_id != actor.id:
                raise PermissionDenied("仅申请人可以撤回")
            instance.status = RequestStatus.WITHDRAWN
        elif action in {"accept", "reject"}:
            if not is_owner:
                raise PermissionDenied("仅项目负责人可以处理申请")
            instance.status = RequestStatus.ACCEPTED if action == "accept" else RequestStatus.REJECTED
            if action == "accept":
                team = instance.project.team
                if team.members.count() >= instance.project.max_members:
                    raise ValidationError("团队人数已满")
                TeamMember.objects.get_or_create(team=team, user=instance.applicant)
        else:
            raise ValidationError("不支持的操作")
    elif isinstance(instance, Invitation):
        if action == "withdraw":
            if instance.inviter_id != actor.id:
                raise PermissionDenied("仅邀请人可以撤回")
            instance.status = RequestStatus.WITHDRAWN
        elif action in {"accept", "reject"}:
            if instance.invitee_id != actor.id:
                raise PermissionDenied("仅被邀请人可以处理邀请")
            instance.status = RequestStatus.ACCEPTED if action == "accept" else RequestStatus.REJECTED
            if action == "accept":
                if instance.team.members.count() >= instance.team.project.max_members:
                    raise ValidationError("团队人数已满")
                TeamMember.objects.get_or_create(team=instance.team, user=instance.invitee)
        else:
            raise ValidationError("不支持的操作")
    instance.save(update_fields=["status", "updated_at"])
    audit(actor, f"{instance.__class__.__name__.lower()}.{action}", instance, status=instance.status)
    return instance

