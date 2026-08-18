import math


class EurocodeEngine:

    @staticmethod
    def beam_analysis(
            span,
            gk,
            qk):

        q_ed = (
            1.35 * gk
            +
            1.50 * qk
        )

        m_ed = (
            q_ed * span**2
        ) / 8

        v_ed = (
            q_ed * span
        ) / 2

        return {
            "q_ed": round(q_ed, 2),
            "m_ed": round(m_ed, 2),
            "v_ed": round(v_ed, 2)
        }
