from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    admins,
    courses,
    divisions,
    login,
    professors,
    schools,
    students,
    terms,
    timeslots,
    users,
    utils,
    years,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admins.router, prefix="/admins", tags=["admins"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(professors.router, prefix="/professors", tags=["professors"])
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(years.router, prefix="/years", tags=["years"])
api_router.include_router(terms.router, prefix="/terms", tags=["terms"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(divisions.router, prefix="/divisions", tags=["divisions"])
api_router.include_router(timeslots.router, prefix="/timeslots", tags=["timeslots"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
