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


def send_notifications(db: Session, recipient_type: str, recipient_ids: List[str], template: str, month: int, year: int, sent_by: str) -> dict:
    """Send email notifications to selected users"""
    
    if recipient_type == "specific":
        users = get_specific_users(db, recipient_ids)
    else:
        users = get_users_by_type(db, recipient_type)
    
    if not users:
        return {
            "sent_count": 0,
            "failed_count": 0,
            "message": "No se encontraron usuarios para enviar notificaciones"
        }
    
    sent_count = 0
    failed_count = 0
    
    print(f"Configuración SMTP - Host: {settings.SMTP_HOST}, Port: {settings.SMTP_PORT}")
    print(f"SMTP User: {settings.SMTP_USER}")
    print(f"SMTP Password repr: {repr(settings.SMTP_PASSWORD)}")
    
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        print("✓ Conexión SMTP establecida")
        
        for user in users:
            try:
                subject, body = get_email_content(template, user.name or "Usuario", month, year)
                print(f"Enviando a {user.email}: {subject}")
                
                msg = MIMEMultipart()
                msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
                msg['To'] = user.email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'html'))
                
                server.sendmail(settings.SMTP_USER, user.email, msg.as_string())
                sent_count += 1
                print(f"✓ Enviado a {user.email}")
            except Exception as e:
                print(f"✗ Error sending to {user.email}: {str(e)}")
                failed_count += 1
        
        server.quit()
        
    except Exception as e:
        print(f"Error initializing email client: {e}")
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