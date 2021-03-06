"""Initial revision

Revision ID: 8769c70e44a7
Revises: 
Create Date: 2021-04-11 17:01:51.271414

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8769c70e44a7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('schools',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('head', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schools_head'), 'schools', ['head'], unique=True)
    op.create_index(op.f('ix_schools_id'), 'schools', ['id'], unique=False)
    op.create_index(op.f('ix_schools_name'), 'schools', ['name'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('profile_picture', sa.String(length=41), nullable=True),
    sa.Column('hashed_password', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('type', postgresql.ENUM('superuser', 'student', 'professor', 'admin', name='user_type'), nullable=False),
    sa.Column('school_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_full_name'), 'users', ['full_name'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_school_id'), 'users', ['school_id'], unique=False)
    op.create_table('years',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('school_id', sa.String(length=36), nullable=False),
    sa.Column('start_year', sa.Integer(), nullable=False),
    sa.Column('end_year', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'school_id', 'start_year', 'end_year')
    )
    op.create_index(op.f('ix_years_end_year'), 'years', ['end_year'], unique=False)
    op.create_index(op.f('ix_years_id'), 'years', ['id'], unique=False)
    op.create_index(op.f('ix_years_name'), 'years', ['name'], unique=False)
    op.create_index(op.f('ix_years_school_id'), 'years', ['school_id'], unique=False)
    op.create_index(op.f('ix_years_start_year'), 'years', ['start_year'], unique=False)
    op.create_table('admins',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('permissions', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_admins_user_id'), 'admins', ['user_id'], unique=False)
    op.create_table('professors',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_professors_user_id'), 'professors', ['user_id'], unique=False)
    op.create_table('terms',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('year_id', sa.String(length=36), nullable=False),
    sa.Column('current_year_term', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('has_electives', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['year_id'], ['years.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_terms_end_date'), 'terms', ['end_date'], unique=False)
    op.create_index(op.f('ix_terms_id'), 'terms', ['id'], unique=False)
    op.create_index(op.f('ix_terms_name'), 'terms', ['name'], unique=False)
    op.create_index(op.f('ix_terms_start_date'), 'terms', ['start_date'], unique=False)
    op.create_index(op.f('ix_terms_year_id'), 'terms', ['year_id'], unique=False)
    op.create_table('courses',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('course_code', sa.String(length=20), nullable=False),
    sa.Column('elective_code', sa.String(length=20), nullable=True),
    sa.Column('term_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['term_id'], ['terms.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'course_code', 'term_id', name='_unique_by_name_code_term')
    )
    op.create_index(op.f('ix_courses_course_code'), 'courses', ['course_code'], unique=False)
    op.create_index(op.f('ix_courses_elective_code'), 'courses', ['elective_code'], unique=False)
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)
    op.create_index(op.f('ix_courses_name'), 'courses', ['name'], unique=False)
    op.create_index(op.f('ix_courses_term_id'), 'courses', ['term_id'], unique=False)
    op.create_table('students',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('term_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['term_id'], ['terms.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_students_term_id'), 'students', ['term_id'], unique=False)
    op.create_index(op.f('ix_students_user_id'), 'students', ['user_id'], unique=False)
    op.create_table('divisions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('course_id', sa.String(length=36), nullable=False),
    sa.Column('division_code', sa.Integer(), nullable=False),
    sa.Column('professor_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['professor_id'], ['professors.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_id', 'division_code', name='_unique_by_course_division')
    )
    op.create_index(op.f('ix_divisions_course_id'), 'divisions', ['course_id'], unique=False)
    op.create_index(op.f('ix_divisions_division_code'), 'divisions', ['division_code'], unique=False)
    op.create_index(op.f('ix_divisions_id'), 'divisions', ['id'], unique=False)
    op.create_index(op.f('ix_divisions_professor_id'), 'divisions', ['professor_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_divisions_professor_id'), table_name='divisions')
    op.drop_index(op.f('ix_divisions_id'), table_name='divisions')
    op.drop_index(op.f('ix_divisions_division_code'), table_name='divisions')
    op.drop_index(op.f('ix_divisions_course_id'), table_name='divisions')
    op.drop_table('divisions')
    op.drop_index(op.f('ix_students_user_id'), table_name='students')
    op.drop_index(op.f('ix_students_term_id'), table_name='students')
    op.drop_table('students')
    op.drop_index(op.f('ix_courses_term_id'), table_name='courses')
    op.drop_index(op.f('ix_courses_name'), table_name='courses')
    op.drop_index(op.f('ix_courses_id'), table_name='courses')
    op.drop_index(op.f('ix_courses_elective_code'), table_name='courses')
    op.drop_index(op.f('ix_courses_course_code'), table_name='courses')
    op.drop_table('courses')
    op.drop_index(op.f('ix_terms_year_id'), table_name='terms')
    op.drop_index(op.f('ix_terms_start_date'), table_name='terms')
    op.drop_index(op.f('ix_terms_name'), table_name='terms')
    op.drop_index(op.f('ix_terms_id'), table_name='terms')
    op.drop_index(op.f('ix_terms_end_date'), table_name='terms')
    op.drop_table('terms')
    op.drop_index(op.f('ix_professors_user_id'), table_name='professors')
    op.drop_table('professors')
    op.drop_index(op.f('ix_admins_user_id'), table_name='admins')
    op.drop_table('admins')
    op.drop_index(op.f('ix_years_start_year'), table_name='years')
    op.drop_index(op.f('ix_years_school_id'), table_name='years')
    op.drop_index(op.f('ix_years_name'), table_name='years')
    op.drop_index(op.f('ix_years_id'), table_name='years')
    op.drop_index(op.f('ix_years_end_year'), table_name='years')
    op.drop_table('years')
    op.drop_index(op.f('ix_users_school_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_full_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_schools_name'), table_name='schools')
    op.drop_index(op.f('ix_schools_id'), table_name='schools')
    op.drop_index(op.f('ix_schools_head'), table_name='schools')
    op.drop_table('schools')
    # ### end Alembic commands ###
