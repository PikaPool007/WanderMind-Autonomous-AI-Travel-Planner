import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
import markdown2
from bs4 import BeautifulSoup
from io import BytesIO

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from src.tools.logger import logger


class DisplayResultStreamlit:
    def __init__(self, graph, user_message):
        self.graph = graph
        self.user_message = user_message
        logger.info("DisplayResultStreamlit initialized with new user message")

    def generate_pdf(self, markdown_text: str) -> bytes:
        """Convert itinerary markdown into a downloadable PDF."""
        logger.info("Generating itinerary PDF...")
        buffer = BytesIO()

        try:
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()

            # Base style modifications
            body_style = styles['BodyText']
            body_style.fontSize = 10
            body_style.leading = 14

            story = []

            # Convert markdown → HTML → extract styled text
            html = markdown2.markdown(markdown_text)
            soup = BeautifulSoup(html, "html.parser")

            for elem in soup.contents:
                if elem.name in ["h1", "h2", "h3"]:
                    style = styles['Heading' + elem.name[1]]
                    story.append(Paragraph(elem.get_text(), style))
                    story.append(Spacer(1, 8))

                elif elem.name == "ul":
                    for li in elem.find_all("li"):
                        story.append(Paragraph("• " + li.get_text(), body_style))
                    story.append(Spacer(1, 6))

                elif elem.name == "ol":
                    for idx, li in enumerate(elem.find_all("li"), start=1):
                        story.append(Paragraph(f"{idx}. {li.get_text()}", body_style))
                    story.append(Spacer(1, 6))

                elif elem.name == "p":
                    story.append(Paragraph(elem.get_text(), body_style))
                    story.append(Spacer(1, 6))

            doc.build(story)
            buffer.seek(0)
            logger.info("✅ PDF generated successfully")
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"❌ Error generating itinerary PDF: {e}", exc_info=True)
            return b""

    def display_result_on_ui(self):
        """Stream results from LangGraph and render them on Streamlit UI."""
        graph = self.graph
        user_message = self.user_message
        logger.info("Displaying results on Streamlit UI")

        with st.chat_message("user"):
            st.write(user_message)
            logger.debug(f"User message displayed: {user_message}")
        with st.spinner("⌛Creating your itinerary..."):
            try:
                for event in graph.stream({"user_data": user_message}):
                    for key, value in event.items():
                        if not value:
                            continue

                        if isinstance(value, dict) and "final_itinerary" in value:
                            itinerary = value["final_itinerary"]
                            with st.chat_message("assistant"):
                                st.markdown("### ✈️ Final Itinerary")
                                st.write(itinerary)

                                # ✅ Generate and show PDF download button
                                pdf_data = self.generate_pdf(itinerary)
                                st.download_button(
                                    label="📄 Download Itinerary as PDF",
                                    data=pdf_data,
                                    file_name="travel_itinerary.pdf",
                                    mime="application/pdf"
                                )
                            logger.info("Final itinerary displayed and PDF download enabled")

                        elif hasattr(value, "content"):
                            with st.chat_message("assistant"):
                                st.write(value.content)
                            logger.debug("Assistant message displayed in stream")

            except Exception as e:
                logger.error(f"❌ Error during UI streaming or rendering: {e}", exc_info=True)
