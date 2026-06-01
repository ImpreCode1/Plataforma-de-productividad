from sqlalchemy.orm import Session
from uuid import UUID
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.models.user import User
from app.models.role import Role, UserRole
from datetime import datetime
from typing import List


MONTH_NAMES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def get_users_by_type(db: Session, recipient_type: str) -> List[User]:
    """Get users based on recipient type (leaders or employees)"""
    
    if recipient_type == "all_leaders":
        leader_role = db.query(Role).filter(Role.name == "LEADER").first()
        if not leader_role:
            return []
        user_ids = db.query(UserRole.user_id).filter(UserRole.role_id == leader_role.id).all()
        user_ids = [u[0] for u in user_ids]
        return db.query(User).filter(User.id.in_(user_ids), User.is_active == True).all()
    
    elif recipient_type == "all_employees":
        employee_role = db.query(Role).filter(Role.name == "EMPLOYEE").first()
        if not employee_role:
            return []
        user_ids = db.query(UserRole.user_id).filter(UserRole.role_id == employee_role.id).all()
        user_ids = [u[0] for u in user_ids]
        return db.query(User).filter(User.id.in_(user_ids), User.is_active == True).all()
    
    return []


def get_specific_users(db: Session, user_ids: List[str]) -> List[User]:
    """Get specific users by their IDs"""
    return db.query(User).filter(User.id.in_(user_ids), User.is_active == True).all()


def format_month_year(month: int, year: int) -> str:
    """Format month and year for display"""
    month_name = MONTH_NAMES[month - 1] if 1 <= month <= 12 else ""
    return f"{month_name} {year}"


def get_email_content(template: str, name: str, month: int, year: int) -> tuple:
    """Get email subject and body based on template"""
    
    month_year = format_month_year(month, year)
    base_url = "https://central.impresistem.com"
    
    if template == "evidence_reminder":
        subject = f"Recordatorio: Sube tus evidencias de {month_year}"
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <tr>
                                <td style="background-color: #2563eb; padding: 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">📋 Recordatorio de Evidencias</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 30px;">
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">Hola <strong>{name}</strong>,</p>
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">
                                        Te recordamos que debes subir las evidencias de tus indicadores del mes de <strong style="color: #2563eb;">{month_year}</strong>.
                                    </p>
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">
                                        Es importante que cargues toda la documentación de soporte antes de que finalice el mes para que tu líder pueda realizar la evaluación correspondiente.
                                    </p>
                                    <div style="text-align: center; margin: 30px 0;">
                                        <a href="{base_url}" style="background-color: #2563eb; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Ingresar a la Plataforma</a>
                                    </div>
                                    <p style="color: #666666; font-size: 14px; line-height: 1.6;">
                                        Si tienes alguna duda, contacta a tu líder o al administrador del sistema.
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f8f8f8; padding: 20px; text-align: center;">
                                    <p style="color: #999999; font-size: 12px; margin: 0;">
                                        © 2026 Impresistem - Sistema de Productividad
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return subject, html_body
    
    elif template == "calification_reminder":
        subject = f"Recordatorio: Califica los indicadores de tu equipo - {month_year}"
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <tr>
                                <td style="background-color: #7c3aed; padding: 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">📊 Recordatorio de Calificación</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 30px;">
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">Hola <strong>{name}</strong>,</p>
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">
                                        Te recordamos que debes calificar los indicadores de tu equipo del mes de <strong style="color: #7c3aed;">{month_year}</strong>.
                                    </p>
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">
                                        Por favor ingresa al panel de líder, revisa el avance de cada colaborador y cierra las evaluaciones antes de que finalice el mes.
                                    </p>
                                    <div style="text-align: center; margin: 30px 0;">
                                        <a href="{base_url}" style="background-color: #7c3aed; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Ingresar a la Plataforma</a>
                                    </div>
                                    <p style="color: #666666; font-size: 14px; line-height: 1.6;">
                                        Si tienes alguna duda, contacta al administrador del sistema.
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f8f8f8; padding: 20px; text-align: center;">
                                    <p style="color: #999999; font-size: 12px; margin: 0;">
                                        © 2026 Impresistem - Sistema de Productividad
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return subject, html_body
    
    else:
        subject = f"Notificación - {month_year}"
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <tr>
                                <td style="background-color: #059669; padding: 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">🔔 Notificación</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 30px;">
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">Hola <strong>{name}</strong>,</p>
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">
                                        Este es un recordatorio del sistema de productividad de <strong>{month_year}</strong>.
                                    </p>
                                    <p style="color: #333333; font-size: 16px; line-height: 1.6;">
                                        Por favor ingresa a la plataforma para verificar tus tareas pendientes.
                                    </p>
                                    <div style="text-align: center; margin: 30px 0;">
                                        <a href="{base_url}" style="background-color: #059669; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Ir a la Plataforma</a>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f8f8f8; padding: 20px; text-align: center;">
                                    <p style="color: #999999; font-size: 12px; margin: 0;">
                                        © 2026 Impresistem - Sistema de Productividad
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return subject, html_body


def send_notifications(db: Session, recipient_type: str, recipient_ids: List[str], filter_area: str = None, template: str = None, month: int = None, year: int = None, sent_by: str = None) -> dict:
    """Send email notifications to selected users"""

    if recipient_type == "specific":
        users = get_specific_users(db, recipient_ids)
    else:
        users = get_users_by_type(db, recipient_type)

    if filter_area:
        from app.modules.users.service import normalize_area
        normalized_filter = normalize_area(filter_area)
        users = [u for u in users if normalize_area(u.area) == normalized_filter]

    if not users:
        return {
            "sent_count": 0,
            "failed_count": 0,
            "message": "No se encontraron usuarios para enviar notificaciones"
        }
    
    sent_count = 0
    failed_count = 0
    
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.ehlo()
        if settings.SMTP_USE_TLS:
            server.starttls()
            server.ehlo()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        for user in users:
            try:
                subject, body = get_email_content(template, user.name or "Usuario", month, year)
                
                from_address = settings.SMTP_FROM if settings.SMTP_FROM else settings.SMTP_USER
                msg = MIMEMultipart()
                msg['From'] = f"{settings.SMTP_FROM_NAME} <{from_address}>"
                msg['To'] = user.email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'html'))
                
                server.sendmail(from_address, user.email, msg.as_string())
                sent_count += 1
            except Exception as e:
                failed_count += 1
        
        server.quit()
        
    except Exception as e:
        error_msg = str(e)
        if "Authentication unsuccessful" in error_msg:
            return {
                "sent_count": 0,
                "failed_count": len(users),
                "message": "Error de autenticación. Verifica que el usuario y contraseña de SMTP sean correctos. Si tienes 2FA en Office 365, usa una App Password en lugar de tu contraseña normal."
            }
        return {
            "sent_count": 0,
            "failed_count": len(users),
            "message": f"Error al conectar con el servidor de correo: {str(e)}"
        }
    
    return {
        "sent_count": sent_count,
        "failed_count": failed_count,
        "message": f"Se enviaron {sent_count} correos exitosamente. {failed_count} fallidos."
    }


# ================================================
# NOTIFICACIONES AUTOMÁTICAS DEL FLUJO DE APROBACIÓN
# ================================================

def _send_single_email(to_email: str, to_name: str, subject: str, html_body: str):
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.ehlo()
        if settings.SMTP_USE_TLS:
            server.starttls()
            server.ehlo()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        from_address = settings.SMTP_FROM if settings.SMTP_FROM else settings.SMTP_USER
        msg = MIMEMultipart()
        msg['From'] = f"{settings.SMTP_FROM_NAME} <{from_address}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        server.sendmail(from_address, to_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False


def notify_leader_submitted(db: Session, tracking, employee: User):
    from app.models.user import User
    from app.models.indicator_assignment import IndicatorAssignment

    month_name = MONTH_NAMES[tracking.month - 1] if 1 <= tracking.month <= 12 else str(tracking.month)
    assignment = db.query(IndicatorAssignment).filter(IndicatorAssignment.id == tracking.assignment_id).first()
    indicator_name = assignment.indicator_name if assignment else "KPI"
    year = tracking.year

    leader = db.query(User).filter(User.id == employee.leader_id).first()
    if not leader or not leader.email:
        return False

    subject = f"{employee.name} ha enviado sus resultados de {month_name} {year}"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background-color:#f4f4f4;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:20px;">
            <tr><td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                    <tr><td style="background-color:#2563eb;padding:30px;text-align:center;">
                        <h1 style="color:#ffffff;margin:0;font-size:24px;">📋 Resultados Enviados</h1>
                    </td></tr>
                    <tr><td style="padding:30px;">
                        <p style="color:#333333;font-size:16px;line-height:1.6;">Hola <strong>{leader.name}</strong>,</p>
                        <p style="color:#333333;font-size:16px;line-height:1.6;">
                            <strong>{employee.name}</strong> ha enviado sus resultados del indicador <strong>{indicator_name}</strong> correspondiente a <strong>{month_name} {year}</strong> para revisión.
                        </p>
                        <p style="color:#333333;font-size:16px;line-height:1.6;">
                            Ingresa al panel de líder para revisar, aprobar o rechazar los resultados.
                        </p>
                        <div style="text-align:center;margin:30px 0;">
                            <a href="https://central.impresistem.com" style="background-color:#2563eb;color:#ffffff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block;">Ir a la Plataforma</a>
                        </div>
                    </td></tr>
                    <tr><td style="background-color:#f8f8f8;padding:20px;text-align:center;">
                        <p style="color:#999999;font-size:12px;margin:0;">© 2026 Impresistem - Sistema de Productividad</p>
                    </td></tr>
                </table>
            </td></tr>
        </table>
    </body>
    </html>
    """

    return _send_single_email(leader.email, leader.name, subject, html_body)


def notify_employee_approved(db: Session, tracking, approver: User):
    from app.models.user import User
    from app.models.indicator_assignment import IndicatorAssignment

    month_name = MONTH_NAMES[tracking.month - 1] if 1 <= tracking.month <= 12 else str(tracking.month)
    assignment = db.query(IndicatorAssignment).filter(IndicatorAssignment.id == tracking.assignment_id).first()
    indicator_name = assignment.indicator_name if assignment else "KPI"
    year = tracking.year

    employee = db.query(User).filter(User.id == tracking.user_id).first()
    if not employee or not employee.email:
        return False

    subject = f"Tu KPI {indicator_name} de {month_name} {year} fue aprobado"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background-color:#f4f4f4;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:20px;">
            <tr><td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                    <tr><td style="background-color:#16a34a;padding:30px;text-align:center;">
                        <h1 style="color:#ffffff;margin:0;font-size:24px;">✅ KPI Aprobado</h1>
                    </td></tr>
                    <tr><td style="padding:30px;">
                        <p style="color:#333333;font-size:16px;line-height:1.6;">Hola <strong>{employee.name}</strong>,</p>
                        <p style="color:#333333;font-size:16px;line-height:1.6;">
                            Tu indicador <strong>{indicator_name}</strong> de <strong>{month_name} {year}</strong> ha sido <strong style="color:#16a34a;">APROBADO</strong> por {approver.name}.
                        </p>
                        <p style="color:#333333;font-size:16px;line-height:1.6;">
                            Puedes ver los resultados en tu dashboard personal.
                        </p>
                        <div style="text-align:center;margin:30px 0;">
                            <a href="https://central.impresistem.com" style="background-color:#16a34a;color:#ffffff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block;">Ver Dashboard</a>
                        </div>
                    </td></tr>
                    <tr><td style="background-color:#f8f8f8;padding:20px;text-align:center;">
                        <p style="color:#999999;font-size:12px;margin:0;">© 2026 Impresistem - Sistema de Productividad</p>
                    </td></tr>
                </table>
            </td></tr>
        </table>
    </body>
    </html>
    """

    return _send_single_email(employee.email, employee.name, subject, html_body)


def notify_employee_rejected(db: Session, tracking, approver: User, comment: str):
    from app.models.user import User
    from app.models.indicator_assignment import IndicatorAssignment

    month_name = MONTH_NAMES[tracking.month - 1] if 1 <= tracking.month <= 12 else str(tracking.month)
    assignment = db.query(IndicatorAssignment).filter(IndicatorAssignment.id == tracking.assignment_id).first()
    indicator_name = assignment.indicator_name if assignment else "KPI"
    year = tracking.year

    employee = db.query(User).filter(User.id == tracking.user_id).first()
    if not employee or not employee.email:
        return False

    subject = f"Tu KPI {indicator_name} de {month_name} {year} fue rechazado"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background-color:#f4f4f4;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:20px;">
            <tr><td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                    <tr><td style="background-color:#dc2626;padding:30px;text-align:center;">
                        <h1 style="color:#ffffff;margin:0;font-size:24px;">❌ KPI Rechazado</h1>
                    </td></tr>
                    <tr><td style="padding:30px;">
                        <p style="color:#333333;font-size:16px;line-height:1.6;">Hola <strong>{employee.name}</strong>,</p>
                        <p style="color:#333333;font-size:16px;line-height:1.6;">
                            Tu indicador <strong>{indicator_name}</strong> de <strong>{month_name} {year}</strong> ha sido <strong style="color:#dc2626;">RECHAZADO</strong> por {approver.name}.
                        </p>
                        <div style="background-color:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:16px;margin:20px 0;">
                            <p style="color:#991b1b;font-size:14px;font-weight:bold;margin:0 0 8px 0;">Comentario del evaluador:</p>
                            <p style="color:#7f1d1d;font-size:14px;margin:0;font-style:italic;">"{comment}"</p>
                        </div>
                        <p style="color:#333333;font-size:16px;line-height:1.6;">
                            Por favor, corrige los valores y/o evidencias según el comentario recibido y vuelve a enviar a revisión.
                        </p>
                        <div style="text-align:center;margin:30px 0;">
                            <a href="https://central.impresistem.com" style="background-color:#dc2626;color:#ffffff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block;">Corregir y Reenviar</a>
                        </div>
                    </td></tr>
                    <tr><td style="background-color:#f8f8f8;padding:20px;text-align:center;">
                        <p style="color:#999999;font-size:12px;margin:0;">© 2026 Impresistem - Sistema de Productividad</p>
                    </td></tr>
                </table>
            </td></tr>
        </table>
    </body>
    </html>
    """

    return _send_single_email(employee.email, employee.name, subject, html_body)