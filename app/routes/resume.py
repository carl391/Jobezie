"""
Resume Routes

API endpoints for resume management and ATS scoring.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.resume_service import ResumeService


resume_bp = Blueprint('resume', __name__, url_prefix='/api/resumes')


@resume_bp.route('', methods=['POST'])
@jwt_required()
def upload_resume():
    """
    Upload a new resume.

    Accepts multipart/form-data with file and optional metadata.

    Returns:
        JSON with resume data and initial ATS score
    """
    user_id = get_jwt_identity()

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    title = request.form.get('title')
    is_master = request.form.get('is_master', 'false').lower() == 'true'

    try:
        resume, ats_result = ResumeService.upload_resume(
            user_id=user_id,
            file=file,
            title=title,
            is_master=is_master,
        )

        return jsonify({
            'message': 'Resume uploaded successfully',
            'resume': resume.to_dict(),
            'ats_analysis': ats_result,
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Resume upload error: {str(e)}")
        return jsonify({'error': 'Failed to process resume'}), 500


@resume_bp.route('', methods=['GET'])
@jwt_required()
def get_resumes():
    """
    Get all resumes for the current user.

    Query params:
        include_deleted: Include soft-deleted resumes (default: false)

    Returns:
        JSON array of resume objects
    """
    user_id = get_jwt_identity()
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

    resumes = ResumeService.get_user_resumes(user_id, include_deleted)

    return jsonify({
        'resumes': [r.to_dict() for r in resumes],
        'count': len(resumes),
    }), 200


@resume_bp.route('/master', methods=['GET'])
@jwt_required()
def get_master_resume():
    """
    Get the user's master resume.

    Returns:
        JSON with master resume data or null if not set
    """
    user_id = get_jwt_identity()
    resume = ResumeService.get_master_resume(user_id)

    if not resume:
        return jsonify({
            'resume': None,
            'message': 'No master resume set'
        }), 200

    return jsonify({
        'resume': resume.to_dict(include_analysis=True),
    }), 200


@resume_bp.route('/<resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """
    Get a specific resume by ID.

    Returns:
        JSON with resume data and ATS analysis
    """
    user_id = get_jwt_identity()
    resume = ResumeService.get_resume(resume_id, user_id)

    if not resume:
        return jsonify({'error': 'Resume not found'}), 404

    return jsonify({
        'resume': resume.to_dict(include_analysis=True),
    }), 200


@resume_bp.route('/<resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """
    Soft delete a resume.

    Returns:
        JSON with success message
    """
    user_id = get_jwt_identity()

    try:
        ResumeService.delete_resume(resume_id, user_id)
        return jsonify({'message': 'Resume deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@resume_bp.route('/<resume_id>/master', methods=['PUT'])
@jwt_required()
def set_master(resume_id):
    """
    Set a resume as the master resume.

    Returns:
        JSON with updated resume data
    """
    user_id = get_jwt_identity()

    try:
        resume = ResumeService.set_master_resume(resume_id, user_id)
        return jsonify({
            'message': 'Master resume updated',
            'resume': resume.to_dict(),
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@resume_bp.route('/<resume_id>/score', methods=['POST'])
@jwt_required()
def score_for_job(resume_id):
    """
    Score a resume against a specific job posting.

    Request body:
        job_keywords: List of keywords from job description
        target_role: Optional target job title

    Returns:
        JSON with job-specific ATS score and recommendations
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    job_keywords = data.get('job_keywords', [])
    target_role = data.get('target_role')

    if not job_keywords:
        return jsonify({'error': 'job_keywords is required'}), 400

    try:
        result = ResumeService.score_for_job(
            resume_id=resume_id,
            user_id=user_id,
            job_keywords=job_keywords,
            target_role=target_role,
        )

        return jsonify({
            'score': result['total_score'],
            'components': result['components'],
            'recommendations': result['recommendations'],
            'missing_keywords': result['missing_keywords'],
            'weak_sections': result['weak_sections'],
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@resume_bp.route('/<resume_id>/tailor', methods=['POST'])
@jwt_required()
def create_tailored_version(resume_id):
    """
    Create a tailored version of a resume for a specific job.

    Request body:
        target_job_title: Required - job title to target
        target_company: Optional - company name
        optimized_text: Optional - AI-optimized resume text

    Returns:
        JSON with new tailored resume data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    target_job_title = data.get('target_job_title')
    if not target_job_title:
        return jsonify({'error': 'target_job_title is required'}), 400

    target_company = data.get('target_company')
    optimized_text = data.get('optimized_text')

    try:
        tailored = ResumeService.create_tailored_version(
            resume_id=resume_id,
            user_id=user_id,
            target_job_title=target_job_title,
            target_company=target_company,
            optimized_text=optimized_text,
        )

        return jsonify({
            'message': 'Tailored resume created',
            'resume': tailored.to_dict(include_analysis=True),
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@resume_bp.route('/<resume_id>/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions(resume_id):
    """
    Get optimization suggestions for a resume.

    Returns:
        JSON with prioritized suggestions and potential score improvement
    """
    user_id = get_jwt_identity()

    try:
        suggestions = ResumeService.get_optimization_suggestions(resume_id, user_id)
        return jsonify(suggestions), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@resume_bp.route('/<resume_id>/analysis', methods=['GET'])
@jwt_required()
def get_analysis(resume_id):
    """
    Get detailed ATS analysis for a resume.

    Returns:
        JSON with full ATS breakdown and component scores
    """
    user_id = get_jwt_identity()
    resume = ResumeService.get_resume(resume_id, user_id)

    if not resume:
        return jsonify({'error': 'Resume not found'}), 404

    return jsonify({
        'resume_id': str(resume.id),
        'title': resume.title,
        'ats_analysis': {
            'total_score': resume.ats_total_score,
            'components': {
                'compatibility': {
                    'score': resume.ats_compatibility_score,
                    'weight': 15,
                    'description': 'File format and parsing compatibility'
                },
                'keywords': {
                    'score': resume.ats_keywords_score,
                    'weight': 15,
                    'description': 'Industry and job-specific keywords'
                },
                'achievements': {
                    'score': resume.ats_achievements_score,
                    'weight': 25,
                    'description': 'Quantified achievements and impact statements'
                },
                'formatting': {
                    'score': resume.ats_formatting_score,
                    'weight': 15,
                    'description': 'Structure, headers, and readability'
                },
                'progression': {
                    'score': resume.ats_progression_score,
                    'weight': 15,
                    'description': 'Career growth and advancement'
                },
                'completeness': {
                    'score': resume.ats_completeness_score,
                    'weight': 10,
                    'description': 'Presence of all essential sections'
                },
                'fit': {
                    'score': resume.ats_fit_score,
                    'weight': 5,
                    'description': 'Alignment with target role'
                },
            },
            'recommendations': resume.ats_recommendations or [],
            'weak_sections': resume.weak_sections or [],
            'missing_keywords': resume.missing_keywords or [],
        }
    }), 200
